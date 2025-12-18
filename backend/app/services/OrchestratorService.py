from typing import Dict, Any
from app.services.FeedbackService import FeedbackService
from app.services.FetcherService import FetcherService
from app.services.HTMLBugsService import HTMLBugsService
from app.services.AccessibilityService import AccessibilityService
from app.services.PerformanceService import PerformanceService 
from app.services.SecurityService import SecurityService

class OrchestratorService:
    """
    Orchestrates all QA services: fetch page → analyze → generate AI report.
    """

    def __init__(self):
        self.fetcher = FetcherService()
        self.html_service = HTMLBugsService()
        self.accessibility_service = AccessibilityService()
        self.performance_service = PerformanceService()
        self.security_service = SecurityService()
        self.feedback_service = FeedbackService()

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Main orchestration method that coordinates all QA checks
        and generates the final AI-powered report.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Comprehensive QA report with AI-generated scores and recommendations
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        
        # Step 1: Fetch the page (never raises exceptions)
        page_data = await self.fetcher.fetch(url)
        
        # If fetch failed, return error response with minimal AI feedback
        if page_data.get('error', False):
            error_qa_data = {
                "final_url": page_data["final_url"],
                "error": True,
                "error_type": page_data.get("error_type"),
                "error_message": page_data.get("error_message"),
                "performance": {"available": False, "message": "Page fetch failed"},
                "security_issues": {"issues": []},
                "accessibility_issues": [],
                "html_bugs": [],
                "seo_data": {}
            }
            
            # Generate feedback even for errors
            feedback_report = await self.feedback_service.generate_feedback(error_qa_data)
            
            return {
                "url": url,
                "final_url": page_data["final_url"],
                "status": page_data["status_code"],
                "error": True,
                "error_type": page_data.get("error_type"),
                "error_message": page_data.get("error_message"),
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_duration": round(time.time() - start_time, 2),
                "report": feedback_report,
                "raw_data": error_qa_data
            }
        
        # Step 2: Analyze all aspects of the page
        html_bugs = self.html_service.analyze(page_data["html"])
        accessibility_issues = self.accessibility_service.analyze(page_data["soup"])
        
        # Performance analysis (skip if page fetch failed)
        performance = {
            "available": False,
            "message": "Skipped",
            "source": "Google PageSpeed Insights",
        }
        
        if not page_data.get("error"):
            performance = await self.performance_service.analyze(page_data["final_url"])
        
        # Security analysis
        security_issues = self.security_service.analyze(
            page_data["soup"], 
            page_data["final_url"]
        )
        
        # Step 3: Prepare comprehensive QA data for AI analysis
        qa_data = {
            "final_url": page_data["final_url"],
            "status": page_data["status_code"],
            "load_time": page_data["load_time"],
            "size_bytes": page_data["size_bytes"],
            "title": page_data["title"],
            "meta_tags": page_data["meta_tags"],
            "performance": performance,
            "security_issues": security_issues,
            "accessibility_issues": accessibility_issues,
            "html_bugs": html_bugs,
            "seo_data": {
                "title": page_data["title"],
                "meta_tags": page_data["meta_tags"],
                "links_count": len(page_data["links"]),
                "images_count": len(page_data["images"]),
                "forms_count": len(page_data["forms"])
            }
        }
        
        # Step 4: Generate AI-powered feedback report
        feedback_report = await self.feedback_service.generate_feedback(qa_data)
        
        # Step 5: Return the AI-generated report directly to frontend
        # The report already contains everything the frontend needs!
        return feedback_report