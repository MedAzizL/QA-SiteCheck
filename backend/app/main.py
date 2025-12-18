from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

import os

# Load .env file BEFORE importing any services
load_dotenv()

# Debug: Verify API key is loaded
api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")
if api_key:
    print(f"✓ API Key loaded: {api_key[:10]}...{api_key[-4:]}")
else:
    print("✗ No API key found in environment!")

from app.api.analyze import router as analyze_router

app = FastAPI(title="QA Site Check")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "api_key_configured": bool(api_key)
    }

@app.get("/")
def root():
    return {
        "message": "QA Site Check API",
        "version": "1.0.0",
        "api_key_configured": bool(api_key)
    }