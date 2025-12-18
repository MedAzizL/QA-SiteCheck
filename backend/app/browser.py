from typing import Optional
from playwright.async_api import Browser

_browser: Optional[Browser] = None

def set_browser(browser: Browser):
    global _browser
    _browser = browser

def get_browser() -> Optional[Browser]:
    return _browser
