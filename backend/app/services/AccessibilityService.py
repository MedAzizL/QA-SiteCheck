from bs4 import BeautifulSoup
from typing import Dict, List, Any

class AccessibilityService:
    """
    Accessibility QA checks following WCAG 2.1 guidelines.
    """

    def analyze(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Run all accessibility checks and return standardized results.
        Returns list format matching HTMLBugsService for consistency.
        """
        issues = []
        
        # 1. Check images alt text
        missing_alt = self._check_images_alt(soup)
        if missing_alt:
            issues.append({
                "type": "error",
                "category": "accessibility",
                "guideline": "WCAG 1.1.1",
                "message": f"Found {len(missing_alt)} image(s) without alt text",
                "count": len(missing_alt),
                "details": missing_alt[:3]  
            })
        
        # 2. Check form labels
        missing_labels = self._check_form_labels(soup)
        if missing_labels:
            issues.append({
                "type": "error",
                "category": "accessibility",
                "guideline": "WCAG 1.3.1",
                "message": f"Found {len(missing_labels)} form input(s) without labels",
                "count": len(missing_labels),
                "details": missing_labels[:3]
            })
        
        # 3. Check heading hierarchy
        heading_issues = self._check_heading_hierarchy(soup)
        if heading_issues:
            issues.append({
                "type": "warning",
                "category": "accessibility",
                "guideline": "WCAG 2.4.6",
                "message": "Heading hierarchy issues detected",
                "count": len(heading_issues),
                "details": heading_issues
            })
        
        # 4. Check link text
        bad_links = self._check_link_text(soup)
        if bad_links:
            issues.append({
                "type": "warning",
                "category": "accessibility",
                "guideline": "WCAG 2.4.4",
                "message": f"Found {len(bad_links)} link(s) with non-descriptive text",
                "count": len(bad_links),
                "details": bad_links[:3]
            })
        
        # 5. Check color contrast (basic check for inline styles)
        contrast_issues = self._check_color_contrast(soup)
        if contrast_issues:
            issues.append({
                "type": "warning",
                "category": "accessibility",
                "guideline": "WCAG 1.4.3",
                "message": "Potential color contrast issues found",
                "count": len(contrast_issues),
                "details": contrast_issues[:3]
            })
        
        # 6. Check language attribute
        if not self._check_lang_attribute(soup):
            issues.append({
                "type": "error",
                "category": "accessibility",
                "guideline": "WCAG 3.1.1",
                "message": "Missing 'lang' attribute on <html> element"
            })
        
        return issues if issues else [{"type": "info", "message": "No accessibility issues detected"}]
    
    def _check_images_alt(self, soup: BeautifulSoup) -> List[str]:
        """Check if all <img> tags have non-empty alt attributes"""
        missing_alt = []
        for img in soup.find_all("img"):
            alt = img.get("alt")
            if alt is None or (isinstance(alt, str) and alt.strip() == ""):
                src = img.get("src", "unknown")
                missing_alt.append(f"<img src='{src[:50]}...'>")
        return missing_alt
    
    def _check_form_labels(self, soup: BeautifulSoup) -> List[str]:
        """Check if form inputs have associated labels"""
        missing_labels = []
        for input_tag in soup.find_all("input"):
            input_type = input_tag.get("type", "text")
            if input_type in ["hidden", "submit", "button"]:
                continue
            
            input_id = input_tag.get("id")
            input_name = input_tag.get("name", "unknown")
            
            # Check for label with matching 'for' attribute
            if input_id:
                label = soup.find("label", attrs={"for": input_id})
                if label:
                    continue
            
            # Check if input is wrapped in a label
            parent_label = input_tag.find_parent("label")
            if parent_label:
                continue
            
            missing_labels.append(f"<input type='{input_type}' name='{input_name}'>")
        
        return missing_labels
    
    def _check_heading_hierarchy(self, soup: BeautifulSoup) -> List[str]:
        """Check heading hierarchy follows proper order"""
        issues = []
        headings = [tag.name for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        
        if not headings:
            return []
        
        # Check for multiple h1s
        h1_count = headings.count("h1")
        if h1_count > 1:
            issues.append(f"Multiple h1 elements found ({h1_count})")
        
        # Check hierarchy
        last_level = 0
        for heading in headings:
            level = int(heading[1])
            if last_level > 0 and level - last_level > 1:
                issues.append(f"Skipped from <{headings[headings.index(heading)-1]}> to <{heading}>")
            last_level = level
        
        return issues
    
    def _check_link_text(self, soup: BeautifulSoup) -> List[str]:
        """Ensure all links have descriptive text"""
        bad_links = []
        non_descriptive = ["click here", "read more", "link", "more", "here"]
        
        for a in soup.find_all("a"):
            text = a.get_text(strip=True).lower()
            href = a.get("href", "#")
            
            if not text:
                bad_links.append(f"<a href='{href[:30]}...'> (empty text)")
            elif text in non_descriptive:
                bad_links.append(f"<a href='{href[:30]}...'>{text}</a>")
        
        return bad_links
    
    def _check_color_contrast(self, soup: BeautifulSoup) -> List[str]:
        """Basic check for potential color contrast issues"""
        issues = []
        
        # Check for light text on light backgrounds (basic heuristic)
        light_colors = ["white", "#fff", "#ffffff", "rgb(255,255,255)", "lightgray", "yellow"]
        
        for elem in soup.find_all(style=True):
            style = elem.get("style", "").lower()
            if "color:" in style:
                # Very basic check - just flag for manual review
                for color in light_colors:
                    if color in style:
                        issues.append(f"Potential contrast issue: {elem.name} with style='{style[:50]}'")
                        break
        
        return issues
    
    def _check_lang_attribute(self, soup: BeautifulSoup) -> bool:
        """Check if <html> element has lang attribute"""
        html_tag = soup.find("html")
        return html_tag is not None and html_tag.get("lang") is not None