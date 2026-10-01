import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.core.config import get_settings
import json
import asyncio

settings = get_settings()

class AsyncGeminiAnalyst:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # 1. FIX: Menggunakan model standar yang paling stabil dan dipastikan ada
            self.model = genai.GenerativeModel('gemini-3.8-flash')
        except Exception as e:
            print(f"GenAI Init Error: {e}")
            self.model = None

    def _clean_json_string(self, raw_str: str) -> str:
        """
        2. FIX: Membersihkan string dari markdown code blocks jika AI berhalusinasi format.
        Terkadang API Gemini mengembalikan format seperti ```json { ... } ```
        """
        cleaned = raw_str.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        return cleaned.strip()

    async def analyze_context(self, macro: dict, sector: str, candidates: list):
        if not self.model:
            return {"insight": "AI Error: Model failed to initialize. Check API Key.", "picks": [], "rationale": {}}

        print("System: AI analyzing market narrative...")
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

        OUTPUT JSON:
        {{
            "insight": "One sentence summary of the trade thesis.",
            "picks": ["TICKER1", "TICKER2"],
            "rationale": {{
                "TICKER1": "Short reason",
                "TICKER2": "Short reason"
            }}
        }}
        """
        
        # 3. FIX: Disable Safety Settings (BLOCK_NONE) untuk mencegah false-positive pada data finansial
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        try:
            # Menjalankan pemanggilan AI secara asynchronous di thread terpisah
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"},
                safety_settings=safety_settings
            )
            
            raw_text = response.text
            clean_text = self._clean_json_string(raw_text)
            
            return json.loads(clean_text)
            
        except json.JSONDecodeError as e:
            # 4. FIX: Enhanced Logging khusus untuk masalah JSON Parse
            print(f"JSON Parse Error: {e} - Raw Output: {response.text}")
            return {"insight": f"AI Parsing Error: Gagal membaca format JSON.", "picks": [], "rationale": {}}
        except ValueError as e:
            # 4. FIX: Menangani kasus dimana response.text tidak bisa diakses (diblokir sistem)
            print(f"AI Block Error: {e}")
            return {"insight": f"AI Blocked Error: Respon API diblokir oleh filter.", "picks": [], "rationale": {}}
        except Exception as e:
            # 4. FIX: Mengirimkan pesan error spesifik kembali ke response (alih-alih hanya "Analysis unavailable")
            print(f"AI General Error: {e}")
            return {"insight": f"AI Error: {str(e)}", "picks": [], "rationale": {}}
