import aiohttp
import asyncio
from typing import Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

class FetcherService:

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch a webpage and extract data for analysis
        
        Args:
            url: The URL to fetch
            
        Returns:
            Dict containing HTML, metadata, and performance metrics
        """
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as response:
                    load_time = time.time() - start_time
                    
                    # Get response data
                    html = await response.text()
                    status_code = response.status
                    headers = dict(response.headers)
                    final_url = str(response.url)
                    
                    # Parse HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract page data
                    page_data = {
                        'url': url,
                        'final_url': final_url,
                        'html': html,
                        'soup': soup,
                        'status_code': status_code,
                        'headers': headers,
                        'load_time': round(load_time, 2),
                        'size_bytes': len(html.encode('utf-8')),
                        'is_https': urlparse(url).scheme == 'https',
                        'domain': urlparse(url).netloc,
                        
                        # Pre-extract common elements for efficiency
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
                    
            except asyncio.TimeoutError:
                raise ValueError(f"Request timed out after {self.timeout} seconds")
            except aiohttp.ClientError as e:
                raise ValueError(f"Failed to fetch URL: {str(e)}")
            except Exception as e:
                raise ValueError(f"Unexpected error fetching URL: {str(e)}")
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags from HTML"""
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            if name and content:
                meta_tags[name] = content
        
        return meta_tags