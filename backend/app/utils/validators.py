from urllib.parse import urlparse
import requests


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False
    
def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url       

def url_exists(url: str) -> bool:
    headers = {"User-Agent": "Mozilla/5.0"}  # pretend to be a browser
    try:
        response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
        return 200 <= response.status_code < 400
    except requests.RequestException:
        return False
    
