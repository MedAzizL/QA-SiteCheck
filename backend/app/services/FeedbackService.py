import os
import json
import httpx
from typing import Dict, Any

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

class FeedbackService:
    """
    QA Specialist LLM service using Claude API.
    Converts QA results into comprehensive scored reports.
    """

    async def generate_feedback(self, qa_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive QA report with scores via Claude AI.
        Falls back to deterministic report if Claude fails.
        """
        if not ANTHROPIC_API_KEY:
            print("⚠️ No Claude API key found, using fallback report")
            return self._fallback_report(qa_result)
        
        try:
            prompt = self._build_prompt(qa_result)
            
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2000,
                "temperature": 0.7,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    ANTHROPIC_API_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
            # Extract text from Claude response
            llm_text = data.get("content", [{}])[0].get("text", "")
            
            # Clean markdown code blocks if present
            llm_text = llm_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            structured = json.loads(llm_text)
            
            # Validate response structure
            if "metrics" in structured and "overall_score" in structured:
                print("✅ Claude AI report generated successfully")
                structured["details"]["ai_powered"] = True
                return structured
            else:
                print("⚠️ Claude response missing required fields, using fallback")
                return self._fallback_report(qa_result)
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Claude JSON parse error: {e}, using fallback")
            return self._fallback_report(qa_result)
        except httpx.HTTPStatusError as e:
            print(f"⚠️ Claude API HTTP error {e.response.status_code}: {e}, using fallback")
            return self._fallback_report(qa_result)
        except Exception as e:
            print(f"⚠️ Claude API error: {e}, using fallback")
            return self._fallback_report(qa_result)

    def _build_prompt(self, qa: Dict[str, Any]) -> str:
        """
        Build comprehensive prompt for Claude to analyze QA results
        """
        return f"""You are a senior web QA specialist with deep expertise in performance, security, accessibility, and code quality.

Analyze the following comprehensive QA results and generate a detailed scored report:

**Website URL:** {qa.get("final_url")}

**Performance Data:**
{json.dumps(qa.get("performance"), indent=2)}

**Accessibility Issues:**
{json.dumps(qa.get("accessibility_issues"), indent=2)}

**Security Issues:**
{json.dumps(qa.get("security_issues"), indent=2)}

**HTML Bugs:**
{json.dumps(qa.get("html_bugs"), indent=2)}

**SEO Data:**
{json.dumps(qa.get("seo_data"), indent=2)}

**Additional Metrics:**
- Load Time: {qa.get("load_time")}
- Page Size: {qa.get("size_bytes")} bytes
- Status Code: {qa.get("status")}

**Your Task:**
Generate a comprehensive JSON report that will be displayed in a beautiful dashboard. The report must include:

1. **Overall Assessment**: Total score (0-100) and letter grade (A-F)
2. **Individual Metrics**: Score each category with visual indicators
3. **Actionable Recommendations**: Priority-based improvements with expected impact
4. **Executive Summary**: Non-technical overview for stakeholders

**Required JSON Structure:**

{{
  "overall_score": <number 0-100>,
  "grade": "<A|B|C|D|F>",
  "status": "<excellent|good|warning|critical>",
  "summary": "<2-3 sentence executive summary for non-technical stakeholders>",
  "metrics": [
    {{
      "name": "Performance",
      "score": <number 0-100>,
      "status": "<excellent|good|warning|critical>",
      "icon": "⚡",
      "description": "<brief assessment of performance metrics>",
      "color": "<hex color based on score>"
    }},
    {{
      "name": "Security",
      "score": <number 0-100>,
      "status": "<excellent|good|warning|critical>",
      "icon": "🔒",
      "description": "<brief assessment of security posture>",
      "color": "<hex color>"
    }},
    {{
      "name": "Accessibility",
      "score": <number 0-100>,
      "status": "<excellent|good|warning|critical>",
      "icon": "♿",
      "description": "<brief assessment of accessibility compliance>",
      "color": "<hex color>"
    }},
    {{
      "name": "Code Quality",
      "score": <number 0-100>,
      "status": "<excellent|good|warning|critical>",
      "icon": "💻",
      "description": "<brief assessment of HTML structure>",
      "color": "<hex color>"
    }},
    {{
      "name": "SEO",
      "score": <number 0-100>,
      "status": "<excellent|good|warning|critical>",
      "icon": "🔍",
      "description": "<brief assessment of search optimization>",
      "color": "<hex color>"
    }}
  ],
  "highlights": [
    "<most critical finding requiring immediate attention>",
    "<second most important finding>",
    "<positive finding or achievement>"
  ],
  "recommendations": [
    {{
      "priority": "<critical|high|medium|low>",
      "category": "<Performance|Security|Accessibility|Code Quality|SEO>",
      "title": "<clear action item title>",
      "description": "<detailed explanation of the recommendation>",
      "impact": "<expected improvement from implementing this>"
    }}
  ],
  "details": {{
    "load_time": "<formatted load time>",
    "total_issues": <count>,
    "critical_issues": <count>,
    "warnings": <count>
  }}
}}

**Scoring Guidelines:**
- 90-100 (A): Excellent - Use color #10b981 (green)
- 75-89 (B): Good - Use color #3b82f6 (blue)
- 50-74 (C): Warning - Use color #f59e0b (yellow/orange)
- 0-49 (D/F): Critical - Use color #ef4444 (red)

**Important:**
- Be thorough but concise in descriptions
- Prioritize recommendations by actual impact
- Use professional but accessible language
- Calculate scores based on the actual data provided
- Include specific numbers in your assessment
- Return ONLY valid JSON, no markdown formatting, no explanations

Generate the report now:"""

    def _fallback_report(self, qa: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligent fallback report using actual QA data.
        Used when Claude API is unavailable or fails.
        """
        metrics = []
        recommendations = []
        highlights = []
        total_score = 0
        
        # Performance metric
        perf = qa.get("performance", {})
        perf_score = perf.get("score", 85) if perf.get("available") else 85
        metrics.append({
            "name": "Performance",
            "score": perf_score,
            "status": self._get_status(perf_score),
            "icon": "⚡",
            "description": f"Load time: {perf.get('load_time', qa.get('load_time', 'N/A'))}",
            "color": self._get_color(perf_score)
        })
        total_score += perf_score

        if perf_score < 70:
            highlights.append(f"Performance score: {perf_score}/100 - optimization needed")
            recommendations.append({
                "priority": "high",
                "category": "Performance",
                "title": "Optimize Page Performance",
                "description": "Reduce blocking scripts, compress images, and optimize assets to improve load times",
                "impact": "Expected 30-50% faster load times"
            })

        # Security metric
        security_issues = qa.get("security_issues", {}).get("issues", [])
        sec_score = max(0, 100 - (len(security_issues) * 15))
        metrics.append({
            "name": "Security",
            "score": sec_score,
            "status": self._get_status(sec_score),
            "icon": "🔒",
            "description": f"{len(security_issues)} security issues detected",
            "color": self._get_color(sec_score)
        })
        total_score += sec_score

        if security_issues:
            highlights.append(f"Security: {len(security_issues)} critical issues require attention")
            recommendations.append({
                "priority": "critical",
                "category": "Security",
                "title": "Fix Security Vulnerabilities",
                "description": "Add missing security headers (CSP, X-Frame-Options), remove inline scripts, ensure secure data transmission",
                "impact": "Protect user data and prevent common web attacks"
            })

        # Accessibility metric
        a11y_issues = qa.get("accessibility_issues", [])
        a11y_score = max(0, 100 - (len(a11y_issues) * 10))
        metrics.append({
            "name": "Accessibility",
            "score": a11y_score,
            "status": self._get_status(a11y_score),
            "icon": "♿",
            "description": f"{len(a11y_issues)} accessibility issues found",
            "color": self._get_color(a11y_score)
        })
        total_score += a11y_score

        if a11y_issues:
            highlights.append(f"Accessibility: {len(a11y_issues)} WCAG violations detected")
            recommendations.append({
                "priority": "medium",
                "category": "Accessibility",
                "title": "Improve Web Accessibility",
                "description": "Add alt text to images, improve color contrast, use semantic HTML, ensure keyboard navigation",
                "impact": "Make your site usable for all users including those with disabilities"
            })

        # Code Quality metric - FIXED: Handle empty array correctly
        html_bugs = qa.get("html_bugs", [])
        if not html_bugs or len(html_bugs) == 0:
            code_score = 95  # No bugs = excellent code quality!
        else:
            code_score = max(0, 100 - (len(html_bugs) * 8))
        
        metrics.append({
            "name": "Code Quality",
            "score": code_score,
            "status": self._get_status(code_score),
            "icon": "💻",
            "description": f"{len(html_bugs)} HTML issues detected" if html_bugs else "Clean HTML structure",
            "color": self._get_color(code_score)
        })
        total_score += code_score

        if html_bugs and len(html_bugs) > 0:
            recommendations.append({
                "priority": "low",
                "category": "Code Quality",
                "title": "Fix HTML Structure Issues",
                "description": "Correct invalid HTML markup, fix nesting errors, ensure valid HTML5 structure",
                "impact": "Better browser compatibility and maintainability"
            })

        # SEO metric
        seo_data = qa.get("seo_data", {})
        has_title = bool(seo_data.get("title"))
        has_meta = bool(seo_data.get("meta_tags"))
        seo_score = 70 + (15 if has_title else 0) + (15 if has_meta else 0)
        
        metrics.append({
            "name": "SEO",
            "score": seo_score,
            "status": self._get_status(seo_score),
            "icon": "🔍",
            "description": "Search engine optimization",
            "color": self._get_color(seo_score)
        })
        total_score += seo_score

        if not has_title or not has_meta:
            recommendations.append({
                "priority": "medium",
                "category": "SEO",
                "title": "Improve SEO Metadata",
                "description": "Add descriptive title tags, meta descriptions, structured data for better search visibility",
                "impact": "Improved search engine rankings and click-through rates"
            })

        overall_score = total_score // 5
        
        # Add positive highlights if score is good
        if overall_score >= 80:
            highlights.insert(0, "✅ Excellent overall performance!")
        elif overall_score >= 60:
            highlights.insert(0, "👍 Good foundation with room for improvement")
        
        if not highlights:
            highlights = ["✅ All critical checks passed", "Site is performing well overall"]

        return {
            "overall_score": overall_score,
            "grade": self._get_grade(overall_score),
            "status": self._get_status(overall_score),
            "summary": f"Website scored {overall_score}/100. " + 
                      ("Excellent work! Minor optimizations recommended." if overall_score >= 80 else
                       "Solid foundation with room for optimization." if overall_score >= 60 else
                       "Several critical issues need immediate attention."),
            "metrics": metrics,
            "highlights": highlights,
            "recommendations": recommendations,
            "details": {
                "load_time": str(qa.get("load_time", "N/A")),
                "total_issues": len(security_issues) + len(a11y_issues) + len(html_bugs),
                "critical_issues": len(security_issues),
                "warnings": len(a11y_issues) + len(html_bugs),
                "ai_powered": False
            }
        }

    def _get_status(self, score: int) -> str:
        """Convert numeric score to status string"""
        if score >= 90: return "excellent"
        if score >= 75: return "good"
        if score >= 50: return "warning"
        return "critical"

    def _get_color(self, score: int) -> str:
        """Get color hex code based on score"""
        if score >= 90: return "#10b981"  # Green
        if score >= 75: return "#3b82f6"  # Blue
        if score >= 50: return "#f59e0b"  # Orange
        return "#ef4444"  # Red

    def _get_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"