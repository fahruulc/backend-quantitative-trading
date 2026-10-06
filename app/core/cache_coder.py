"""
Shared fastapi-cache coder that tolerates Redis clients configured with
decode_responses=True (cached value comes back as str, not bytes).
"""
import json
from fastapi_cache.coder import JsonCoder


class SafeJsonCoder(JsonCoder):
    @classmethod
    def decode(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return super().decode(value)
