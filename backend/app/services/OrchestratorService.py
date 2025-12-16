from app.services.FetcherService import FetcherService
from app.services.HTMLBugsService import HTMLBugsService
from typing import Dict, Any

class OrchestratorService:
    """
    Orchestrates all QA services: fetch page → analyze HTML.
    """
    def __init__(self):
        self.fetcher = FetcherService()
        self.html_service = HTMLBugsService()
    
    async def analyze_url(self, url: str) -> Dict[str, Any]:
        # Fetch the page (never raises exceptions)
        page_data = await self.fetcher.fetch(url)
        
        # If fetch failed, return minimal error response
        if page_data.get('error', False):
            return {
                "url": url,
                "final_url": page_data["final_url"],
                "status": page_data["status_code"],
                "error": True,
                "error_type": page_data.get("error_type"),
                "error_message": page_data.get("error_message"),
                "load_time": 0,
                "size_bytes": 0,
                "title": page_data.get("title"),
                "domain": page_data["domain"],
                "links_count": 0,
                "images_count": 0,
                "forms_count": 0,
                "html_bugs": []
            }
        
        # Analyze HTML for bugs
        html_bugs = self.html_service.analyze(page_data["html"])
        
        # Return full QA result
        return {
            "url": url,
            "final_url": page_data["final_url"],
            "status": page_data["status_code"],
            "error": False,
            "load_time": page_data["load_time"],
            "size_bytes": page_data["size_bytes"],
            "title": page_data["title"],
            "meta_tags": page_data["meta_tags"],
            "links_count": len(page_data["links"]),
            "images_count": len(page_data["images"]),
            "forms_count": len(page_data["forms"]),
            "html": page_data["html"],
            "html_bugs": html_bugs,
        }