import os
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class SecurityService:
    """
    PRIMARY: VirusTotal URL reputation
    FALLBACK: Static HTML security checks
    """

    def __init__(self):
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.vt_available = bool(self.api_key)

    # =========================
    # PUBLIC ENTRY
    # =========================
    def analyze(
        self,
        soup: BeautifulSoup,
        url: str,
        headers: Dict = None
    ) -> Dict[str, Any]:

        result = {
            "primary_check": "VirusTotal",
            "fallback_used": False,
            "issues": []
        }

        # 1️⃣ Try VirusTotal first
        if self.vt_available:
            try:
                vt_issue = self._check_virustotal(url)
                result["issues"].append(vt_issue)

                if vt_issue["type"] == "critical":
                    return result

            except Exception:
                result["fallback_used"] = True
        else:
            result["fallback_used"] = True

        # 2️⃣ Fallback static checks
        static_issues = self._static_html_checks(soup, url, headers)
        result["issues"].extend(static_issues)

        if not result["issues"]:
            result["issues"].append({
                "type": "info",
                "category": "security",
                "message": "No security issues detected"
            })

        return result

    # =========================
    # VIRUSTOTAL
    # =========================
    def _check_virustotal(self, url: str) -> Dict[str, Any]:
        headers = {
            "x-apikey": self.api_key
        }

        # Encode URL (VirusTotal requirement)
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        response = requests.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 404:
            # URL not analyzed yet → submit
            requests.post(
                "https://www.virustotal.com/api/v3/urls",
                headers=headers,
                data={"url": url},
                timeout=10
            )

            return {
                "type": "info",
                "category": "security",
                "source": "VirusTotal",
                "message": "URL submitted to VirusTotal for analysis"
            }

        data = response.json()
        stats = data["data"]["attributes"]["last_analysis_stats"]

        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)

        if malicious > 0 or suspicious > 0:
            return {
                "type": "critical",
                "category": "security",
                "source": "VirusTotal",
                "message": "URL flagged as malicious or suspicious",
                "details": stats
            }

        return {
            "type": "info",
            "category": "security",
            "source": "VirusTotal",
            "message": "URL not flagged by VirusTotal"
        }

    # =========================
    # STATIC HTML FALLBACK
    # =========================
    def _static_html_checks(
        self,
        soup: BeautifulSoup,
        url: str,
        headers: Dict = None
    ) -> List[Dict[str, Any]]:

        issues = []
        headers = headers or {}

        if not self._is_https(url):
            issues.append({
                "type": "critical",
                "category": "security",
                "message": "Site is not using HTTPS"
            })

        missing_headers = self._missing_headers(headers)
        if missing_headers:
            issues.append({
                "type": "high",
                "category": "security",
                "message": "Missing security headers",
                "details": missing_headers
            })

        inline_scripts = self._count_inline_scripts(soup)
        if inline_scripts > 0:
            issues.append({
                "type": "medium",
                "category": "security",
                "message": f"{inline_scripts} inline scripts detected"
            })

        return issues

    # =========================
    # HELPERS
    # =========================
    def _is_https(self, url: str) -> bool:
        return urlparse(url).scheme == "https"

    def _missing_headers(self, headers: Dict) -> List[str]:
        required = [
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-Content-Type-Options",
            "Referrer-Policy"
        ]
        return [h for h in required if h not in headers]

    def _count_inline_scripts(self, soup: BeautifulSoup) -> int:
        return sum(
            1 for s in soup.find_all("script")
            if not s.get("src") and s.string
        )
