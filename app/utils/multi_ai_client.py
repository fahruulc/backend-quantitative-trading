from anthropic import AsyncAnthropic
from app.core.config import get_settings
import json
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class MultiAIClient:
    """
    Unified AI client that:
    1. Uses Octalabs router with Anthropic SDK format
    2. Auto-fallback to next model on failure
    3. Logs which model succeeded
    """

    def __init__(self):
        self.base_url = settings.OCTALABS_BASE_URL
        self.api_key = settings.OCTALABS_API_KEY

        # Priority order from list model.txt
        self.models = [
            model.strip()
            for model in settings.AI_MODELS.split(',')
            if model.strip()
        ]

        self.client = AsyncAnthropic(
            base_url=self.base_url,
            api_key=self.api_key
        )

    async def analyze_context_with_fallback(
        self,
        macro: dict,
        sector: str,
        candidates: list,
        max_retries: int = None
    ) -> dict:
        """
        Try multiple AI models until one succeeds

        Args:
            macro: Macro data dictionary
            sector: Selected sector name
            candidates: List of candidate ticker symbols
            max_retries: Maximum number of models to try (default from settings)

        Returns:
            Dictionary with insight, picks, rationale, and model_used
        """

        if max_retries is None:
            max_retries = settings.AI_MAX_RETRIES

        # Demo mode bypass
        if settings.DEMO_MODE and settings.USE_MOCK_DATA:
            logger.info("🎭 DEMO MODE: Using mock AI response")
            return {
                "insight": "[MOCK] Demo mode active",
                "picks": candidates[:2] if len(candidates) >= 2 else candidates,
                "rationale": {
                    candidates[0]: "Mock reason 1" if len(candidates) > 0 else "",
                    candidates[1]: "Mock reason 2" if len(candidates) > 1 else ""
                },
                "model_used": "MOCK"
            }

        prompt = f"""
ROLE: Institutional Equity Strategist.
TASK: Select exactly 2 stocks from the list based on MACRO DRIVERS.

INPUT DATA:
- Macro: {json.dumps(macro)}
- Sector: {sector}
- Candidates: {candidates}

INSTRUCTIONS:
1. Identify the sub-industry most benefited by the specific Macro data.
2. Select 2 tickers that have the highest correlation to these drivers.
3. Rationale must be very short (max 5 words) for table display.

OUTPUT JSON (respond ONLY with valid JSON, no markdown):
{{
    "insight": "One sentence summary of the trade thesis.",
    "picks": ["TICKER1", "TICKER2"],
    "rationale": {{
        "TICKER1": "Short reason",
        "TICKER2": "Short reason"
    }}
}}
"""

        last_error = None

        for i, model in enumerate(self.models[:max_retries]):
            try:
                logger.info(f"🤖 Trying AI model: {model} (attempt {i+1}/{max_retries})")

                response = await self.client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

                # Extract text from response
                content = response.content[0].text

                # Clean markdown code blocks if present
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                # Parse JSON
                result = json.loads(content)
                result["model_used"] = model

                logger.info(f"✅ SUCCESS with model: {model}")
                return result

            except json.JSONDecodeError as e:
                last_error = f"JSON parse error with {model}: {e}"
                logger.warning(f"⚠️ {last_error}, trying next model...")
                continue

            except Exception as e:
                last_error = f"Error with {model}: {str(e)}"
                logger.warning(f"⚠️ {last_error}, trying next model...")
                continue

        # All models failed
        logger.error(f"❌ All AI models failed. Last error: {last_error}")
        return {
            "insight": f"AI Error: All models failed. Last: {last_error}",
            "picks": [],
            "rationale": {},
            "model_used": "NONE"
        }
