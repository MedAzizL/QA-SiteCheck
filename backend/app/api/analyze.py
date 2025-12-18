from fastapi import APIRouter , HTTPException  
from app.utils.validators import is_valid_url , normalize_url
from app.services.OrchestratorService import OrchestratorService
router = APIRouter()
orchestrator = OrchestratorService()

@router.post("/analyze")
async def analyze_url(payload:dict):
    url = payload.get("url")
    if not url :
        raise HTTPException(status_code=400, detail="URL is required")
    
    url=normalize_url(url)


    if not is_valid_url(url) :
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    result = await orchestrator.analyze_url(url)
    return result




    