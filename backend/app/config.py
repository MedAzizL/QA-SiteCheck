"""
Central configuration module.
Loads environment variables once.
Never prints secrets.
"""

from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
