from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright

from app.api.analyze import router as analyze_router
from app.browser import set_browser, get_browser
from app.config import (
    GOOGLE_PAGESPEED_API_KEY,
    VIRUSTOTAL_API_KEY,
    ANTHROPIC_API_KEY,
)

app = FastAPI(title="QA Site Check")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://qa-sitecheck-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- PLAYWRIGHT ----------------
@app.on_event("startup")
async def startup_event():
    try:
        print("🚀 Starting Playwright browser...")
        pw = await async_playwright().start()

        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
            ],
        )

        set_browser(browser)
        print("✅ Playwright browser ready")

    except Exception as e:
        # This is EXPECTED on some Render instances
        print(f"⚠️ Playwright disabled, using HTTP fallback only: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    browser = get_browser()
    if browser:
        await browser.close()
        print("🛑 Playwright browser closed")

# ---------------- ROUTES ----------------
app.include_router(analyze_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "browser_active": get_browser() is not None,
        "pagespeed_configured": bool(GOOGLE_PAGESPEED_API_KEY),
        "virustotal_configured": bool(VIRUSTOTAL_API_KEY),
        "ai_configured": bool(ANTHROPIC_API_KEY),
    }

@app.get("/")
def root():
    return {
        "message": "QA Site Check API",
        "version": "1.0.0",
    }
