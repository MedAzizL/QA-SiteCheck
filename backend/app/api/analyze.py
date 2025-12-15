from fastapi import APIRouter , HTTPException  
from app.utils.validators import is_valid_url, url_exists , normalize_url
router = APIRouter()
@router.post("/analyze")
def analyze_url(payload:dict):
    url = payload.get("url")
    if not url :
        raise HTTPException(status_code=400, detail="URL is required")
    
    url=normalize_url(url)

    if not is_valid_url(url) or not url_exists(url):
        raise HTTPException(status_code=400, detail="URL is not reachable")

    return {"url": url, "status": "valid"}


