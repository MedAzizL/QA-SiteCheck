from app.config import GOOGLE_PAGESPEED_API_KEY
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import time
import asyncio


PAGESPEED_COOLDOWN_SECONDS = 10


class PerformanceService:
    """
    Performance analysis service

    PRIMARY:
      - Google PageSpeed Insights API

    FALLBACK (FREE):
      - Lightweight HTTP timing + HTML size heuristic
    """

    PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    CACHE_DURATION = timedelta(hours=6)

    # Global protection
    _semaphore = asyncio.Semaphore(1)
    _last_call_ts: float = 0.0
    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_PAGESPEED_API_KEY

    # =========================
    # PUBLIC ENTRY POINT
    # =========================
    async def analyze(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        if not self.api_key:
            return await self._fallback_performance_check(
                url, reason="Missing PageSpeed API key"
            )

        key = self._cache_key(url, strategy)

        # 1️⃣ CACHE FIRST
        if key in self._cache and self._cache_valid(self._cache[key]):
            cached = self._cache[key]["data"].copy()
            cached["cached"] = True
            return cached

        # 2️⃣ GLOBAL COOLDOWN
        now = time.time()
        if now - PerformanceService._last_call_ts < PAGESPEED_COOLDOWN_SECONDS:
            wait = PAGESPEED_COOLDOWN_SECONDS - (now - PerformanceService._last_call_ts)
            return await self._fallback_performance_check(
                url, reason=f"Cooldown active ({wait:.1f}s)"
            )

        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
            "key": self.api_key,
        }

        try:
            async with PerformanceService._semaphore:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(self.PAGESPEED_API, params=params)

                PerformanceService._last_call_ts = time.time()

                if response.status_code == 429:
                    return await self._fallback_performance_check(
                        url, reason="PageSpeed rate limit"
                    )

                if response.status_code == 400:
                    msg = response.json().get("error", {}).get("message", "Bad request")
                    return await self._fallback_performance_check(
                        url, reason=f"Bad request: {msg}"
                    )

                response.raise_for_status()
                parsed = self._parse_pagespeed(response.json())

                # Cache successful result
                self._cache[key] = {
                    "data": parsed,
                    "cached_at": datetime.utcnow(),
                }

                return parsed

        except httpx.TimeoutException:
            return await self._fallback_performance_check(
                url, reason="PageSpeed timeout"
            )
        except Exception as e:
            return await self._fallback_performance_check(
                url, reason=str(e)
            )

    # =========================
    # PRIMARY: PAGESPEED PARSER
    # =========================
    def _parse_pagespeed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        score = int(categories.get("performance", {}).get("score", 0) * 100)

        return {
            "available": True,
            "fallback": False,
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

    # =========================
    # FALLBACK (FREE)
    # =========================
    async def _fallback_performance_check(
        self,
        url: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Lightweight performance fallback (no external API)
        """

        try:
            start = time.perf_counter()

            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url)

            ttfb = time.perf_counter() - start
            size_kb = len(response.content) / 1024

            score = self._estimate_score(ttfb, size_kb)

            return {
                "available": True,
                "fallback": True,
                "score": score,
                "grade": self._grade(score),
                "metrics": {
                    "ttfb": round(ttfb, 2),
                    "html_size_kb": round(size_kb, 1),
                },
                "source": "Lightweight HTTP Performance Check",
                "note": f"Fallback used: {reason}",
            }

        except Exception as e:
            return {
                "available": False,
                "fallback": True,
                "source": "Lightweight HTTP Performance Check",
                "message": f"Fallback failed: {str(e)}",
            }

    # =========================
    # HELPERS
    # =========================
    def _estimate_score(self, ttfb: float, size_kb: float) -> int:
        score = 100

        # TTFB penalties
        if ttfb > 1.5:
            score -= 30
        elif ttfb > 1.0:
            score -= 20
        elif ttfb > 0.7:
            score -= 10

        # HTML size penalties
        if size_kb > 500:
            score -= 20
        elif size_kb > 300:
            score -= 10

        return max(30, min(score, 100))

    def _grade(self, score: int) -> str:
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"

    def _cache_key(self, url: str, strategy: str) -> str:
        return hashlib.md5(f"{url}:{strategy}".encode()).hexdigest()

    def _cache_valid(self, entry: Dict[str, Any]) -> bool:
        return datetime.utcnow() - entry["cached_at"] < self.CACHE_DURATION
