from fastapi import APIRouter
from app.utils.validators import is_valid_url_

router = APIRouter()
@router.post("/analyze")
def analyze_url(payload:dict):
    url = payload.get("url")
    if not url or not is_valid_url_(url):
        raise HttpException(status_code=400, detail="Invalid URL")
    
    return {"url": url, "status": "valid"}