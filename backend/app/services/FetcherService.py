from app.browser import get_browser
from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import asyncio

class FetcherService:

    def __init__(self, timeout: int = 60, max_retries: int = 2):
        """
        timeout: in seconds, default 60
        max_retries: number of retry attempts for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch a webpage with retry logic and comprehensive error handling.
        Never raises exceptions - always returns a valid response dict.
        """
        for attempt in range(self.max_retries + 1):
            try:
                return await self._fetch_attempt(url)
            except Exception as e:
                error_str = str(e)
                
                # Don't retry on DNS failures - domain doesn't exist
                if 'ERR_NAME_NOT_RESOLVED' in error_str:
                    return self._create_error_response(url, 'dns_error', error_str)
                
                # Last attempt - return error response
                if attempt == self.max_retries:
                    print("⚠️ Playwright failed — using HTTP fallback")
                    return await self._http_fallback(url, error_str)
                
                # Retry with exponential backoff
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed for {url}, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

    def _create_error_response(self, url: str, error_type: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        status_map = {
            'dns_error': 404,
            'timeout': 408,
            'ssl_error': 526,
            'connection_refused': 503,
            'fetch_failed': 500
        }
        
        return {
            'url': url,
            'final_url': url,
            'html': '',
            'soup': BeautifulSoup('', 'html.parser'),
            'status_code': status_map.get(error_type, 500),
            'load_time': 0,
            'size_bytes': 0,
            'is_https': urlparse(url).scheme == 'https',
            'domain': urlparse(url).netloc,
            'title': None,
            'meta_tags': {},
            'images': [],
            'links': [],
            'forms': [],
            'scripts': [],
            'stylesheets': [],
            'headings': {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []},
            'error': True,
            'error_type': error_type,
            'error_message': error_message
        }


    
    

    async def _fetch_attempt(self, url: str) -> Dict[str, Any]:
        start_time = time.time()
        browser = get_browser()

        # 1️⃣ If browser unavailable → HTTP fallback
        if not browser:
            return await self._http_fallback(url, "Browser not initialized")

        try:
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            page = await context.new_page()

            response = await page.goto(
                url,
                timeout=self.timeout * 1000,
                wait_until="domcontentloaded",
            )

            await page.wait_for_timeout(2000)

            html = await page.content()
            load_time = round(time.time() - start_time, 2)

            soup = BeautifulSoup(html, "html.parser")

            return {
                "url": url,
                "final_url": page.url,
                "html": html,
                "soup": soup,
                "status_code": response.status if response else 0,
                "load_time": load_time,
                "size_bytes": len(html.encode("utf-8")),
                "is_https": urlparse(url).scheme == "https",
                "domain": urlparse(url).netloc,
                "title": soup.title.string if soup.title else None,
                "meta_tags": self._extract_meta_tags(soup),
                "images": soup.find_all("img"),
                "links": soup.find_all("a"),
                "forms": soup.find_all("form"),
                "scripts": soup.find_all("script"),
                "stylesheets": soup.find_all("link", rel="stylesheet"),
                "headings": {
                    "h1": soup.find_all("h1"),
                    "h2": soup.find_all("h2"),
                    "h3": soup.find_all("h3"),
                    "h4": soup.find_all("h4"),
                    "h5": soup.find_all("h5"),
                    "h6": soup.find_all("h6"),
                },
                "error": False,
                "mode": "playwright",
            }

        except Exception as e:
            return await self._http_fallback(url, str(e))

        finally:
            try:
                await page.close()
                await context.close()
            except Exception:
                pass


    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags from HTML"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content
        return meta_tags
    
    async def _http_fallback(self, url: str, error: str):
        """
        HTTP fallback when Playwright is blocked (Render / bot-protected sites).
        Keeps analysis functional instead of returning 0 scores.
        """
        import httpx
        import time
        from bs4 import BeautifulSoup
        from urllib.parse import urlparse

        start_time = time.time()

        try:
            async with httpx.AsyncClient(
                timeout=20.0,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }
            ) as client:
                response = await client.get(url)

            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            final_url = str(response.url)
            parsed = urlparse(final_url)

            return {
                "url": url,
                "final_url": final_url,
                "html": html,
                "soup": soup,
                "status_code": response.status_code,
                "load_time": round(time.time() - start_time, 2),
                "size_bytes": len(response.content),
                "is_https": parsed.scheme == "https",
                "domain": parsed.netloc,
                "title": soup.title.string if soup.title else None,
                "meta_tags": self._extract_meta_tags(soup),
                "images": soup.find_all("img"),
                "links": soup.find_all("a"),
                "forms": soup.find_all("form"),
                "scripts": soup.find_all("script"),
                "stylesheets": soup.find_all("link", rel="stylesheet"),
                "headings": {
                    "h1": soup.find_all("h1"),
                    "h2": soup.find_all("h2"),
                    "h3": soup.find_all("h3"),
                    "h4": soup.find_all("h4"),
                    "h5": soup.find_all("h5"),
                    "h6": soup.find_all("h6"),
                },
                "error": False,
                "error_type": None,
                "error_message": None,
                "note": "HTTP fallback used (Playwright blocked)"
            }

        except Exception as e:
            return self._create_error_response(
                url,
                "fetch_failed",
                f"HTTP fallback failed: {str(e)}"
            )
