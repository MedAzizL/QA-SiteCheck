from fastapi import APIRouter , HTTPException  
from app.utils.validators import is_valid_url , normalize_url
from app.services.FetcherService import  FetcherService 
router = APIRouter()
@router.post("/analyze")
async def analyze_url(payload:dict):
    url = payload.get("url")
    if not url :
        raise HTTPException(status_code=400, detail="URL is required")
    
    url=normalize_url(url)


    if not is_valid_url(url) :
        raise HTTPException(status_code=400, detail="Invalid URL format")

    fetcher=FetcherService()
    page_data= await fetcher.fetch(url)


    return {
        "url": url,
        "status": page_data["status_code"],
        "load_time": page_data["load_time"],
        "size_bytes": page_data["size_bytes"],
        "title": page_data["title"]
    }
