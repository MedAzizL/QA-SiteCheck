from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router
from app.config import (
    GOOGLE_PAGESPEED_API_KEY,
    VIRUSTOTAL_API_KEY,
    ANTHROPIC_API_KEY,
)

app = FastAPI(title="QA Site Check")

# CORS (simple, correct)
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

# ROUTERS (THIS WAS THE PROBLEM)
app.include_router(analyze_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
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
