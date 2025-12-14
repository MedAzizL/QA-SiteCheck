from fastapi import APIRouter
router = APIRouter()
@router.post("/analyze")
def analyze_url(payload:dict):
    url = payload.get("url")
    return {"url": url, "analysis": "not implemented yet"}