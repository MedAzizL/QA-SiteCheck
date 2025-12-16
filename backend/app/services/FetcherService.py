# app/services/FetcherService.py
from playwright.async_api import async_playwright
from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

class FetcherService:

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch a webpage using Playwright and extract HTML, metadata, and performance info.
        Handles bot protection pages like Cloudflare.
        """
        start_time = time.time()
        async with async_playwright() as p:
            # Use Chromium in headful mode
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Set realistic headers to mimic a real user
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
            })

            try:
                # Navigate to the page
                response = await page.goto(url, timeout=self.timeout * 1000)
                await page.wait_for_load_state('networkidle')  # wait for JS to finish

                load_time = time.time() - start_time
                html = await page.content()
                status_code = response.status if response else 0
                final_url = page.url

                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')

                # Extract page data
                page_data = {
                    'url': url,
                    'final_url': final_url,
                    'html': html,
                    'soup': soup,
                    'status_code': status_code,
                    'load_time': round(load_time, 2),
                    'size_bytes': len(html.encode('utf-8')),
                    'is_https': urlparse(url).scheme == 'https',
                    'domain': urlparse(url).netloc,
                    'title': soup.title.string if soup.title else None,
                    'meta_tags': self._extract_meta_tags(soup),
                    'images': soup.find_all('img'),
                    'links': soup.find_all('a'),
                    'forms': soup.find_all('form'),
                    'scripts': soup.find_all('script'),
                    'stylesheets': soup.find_all('link', rel='stylesheet'),
                    'headings': {
                        'h1': soup.find_all('h1'),
                        'h2': soup.find_all('h2'),
                        'h3': soup.find_all('h3'),
                        'h4': soup.find_all('h4'),
                        'h5': soup.find_all('h5'),
                        'h6': soup.find_all('h6')
                    }
                }

                return page_data

            finally:
                await browser.close()
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags from HTML"""
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content
        return meta_tags


