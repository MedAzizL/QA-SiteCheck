from app.config import GOOGLE_PAGESPEED_API_KEY
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import time
import asyncio

PAGESPEED_SEMAPHORE = asyncio.Semaphore(1)
PAGESPEED_COOLDOWN_SECONDS = 10


class PerformanceService:
    PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    CACHE_DURATION = timedelta(hours=6)

    _last_call_ts: float = 0.0

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_PAGESPEED_API_KEY
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _cache_key(self, url: str, strategy: str) -> str:
        return hashlib.md5(f"{url}:{strategy}".encode()).hexdigest()

    def _cache_valid(self, entry: Dict[str, Any]) -> bool:
        return datetime.utcnow() - entry["cached_at"] < self.CACHE_DURATION

    async def analyze(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        if not self.api_key:
            return self._unavailable("Missing API key")

        key = self._cache_key(url, strategy)

        # ✅ 1. CACHE FIRST (MOST IMPORTANT)
        if key in self._cache and self._cache_valid(self._cache[key]):
            cached = self._cache[key]["data"].copy()
            cached["cached"] = True
            return cached

        # ✅ 2. GLOBAL COOLDOWN (ANTI-429)
        now = time.time()
        if now - self._last_call_ts < PAGESPEED_COOLDOWN_SECONDS:
            return self._unavailable("PageSpeed cooldown active")

        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
            "key": self.api_key,
        }

        try:
            async with PAGESPEED_SEMAPHORE:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.get(self.PAGESPEED_API, params=params)

            self._last_call_ts = time.time()

            if response.status_code == 429:
                return self._unavailable("Google PageSpeed rate limit")

            response.raise_for_status()
            parsed = self._parse(response.json())

            self._cache[key] = {
                "data": parsed,
                "cached_at": datetime.utcnow(),
            }

            return parsed

        except Exception:
            return self._unavailable("PageSpeed unavailable")

    def _parse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        score = int(categories.get("performance", {}).get("score", 0) * 100)

        return {
            "available": True,
            "score": score,
            "grade": self._grade(score),
            "metrics": {
                "lcp": audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
                "fcp": audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000,
                "cls": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
                "tbt": audits.get("total-blocking-time", {}).get("numericValue", 0),
            },
            "source": "Google PageSpeed Insights",
            "cached": False,
        }

    def _grade(self, score: int) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    def _unavailable(self, message: str) -> Dict[str, Any]:
        return {
            "available": False,
            "message": message,
            "source": "Google PageSpeed Insights",
        }
