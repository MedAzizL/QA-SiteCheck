import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import html5lib
import re


class HTMLBugsService:
    W3C_VALIDATOR_URL = "https://validator.w3.org/nu/"

    def analyze(self, html: str):
        try:
            
            response = requests.post(
                self.W3C_VALIDATOR_URL,
                params={'out': 'json'},
                data=html.encode('utf-8'),
                headers={"Content-Type": "text/html; charset=utf-8", "User-Agent": "QA-SiteCheck/1.0"}
            )
            response.raise_for_status()
        
            data = response.json()
        
            bugs = [
            {"type": msg.get("type"), "message": msg.get("message")}
            for msg in data.get('messages', [])
            if msg['type'] in ['error', 'warning']
            ]   
            return bugs or [{"type": "info", "message": "No HTML bugs found"}]
        except (requests.RequestException, ValueError, KeyError):
            # W3C API failed - fallback to local validation
            return self._local_validation(html)
        
    def _local_validation(self, html: str) -> List[Dict[str, Any]]:
        """
        Local HTML validation using html5lib and BeautifulSoup.
        """
        bugs = [] 
        bugs.append({"type": "info", "message": "Local HTML validation started"})
        """
        # Parse with html5lib for errors
        try:
            html5lib.parse(html, treebuilder='etree', namespaceHTMLElements=False)
        except Exception as e:
            bugs.append({
                "type": "error",
                "message": f"HTML parsing failed: {str(e)}"
            })"""
        
        # Parse with BeautifulSoup for checks
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check DOCTYPE
        if not self._has_doctype(html):
            bugs.append({
                "type": "warning",
                "message": "Missing or invalid DOCTYPE declaration"
            })
        
        # Check essential tags
        if not soup.find('html'):
            bugs.append({"type": "error", "message": "Missing <html> element"})
        
        if not soup.find('head'):
            bugs.append({"type": "error", "message": "Missing <head> element"})
        
        if not soup.find('body'):
            bugs.append({"type": "error", "message": "Missing <body> element"})
        
        if not soup.find('title'):
            bugs.append({"type": "error", "message": "Missing <title> element"})
        
        # Check charset
        charset_meta = soup.find('meta', charset=True) or soup.find('meta', {'http-equiv': 'Content-Type'})
        if not charset_meta:
            bugs.append({
                "type": "warning",
                "message": "Missing character encoding declaration"
            })
        
        # Check duplicate IDs
        duplicate_ids = self._find_duplicate_ids(soup)
        for dup_id in duplicate_ids:
            bugs.append({
                "type": "error",
                "message": f"Duplicate ID '{dup_id}' found"
            })
        
        # Check images without alt
        imgs_without_alt = soup.find_all('img', alt=False)
        if imgs_without_alt:
            bugs.append({
                "type": "warning",
                "message": f"Found {len(imgs_without_alt)} <img> without 'alt' attribute"
            })
        
        # Check deprecated tags
        deprecated = ['center', 'font', 'marquee', 'blink', 'big', 'strike']
        for tag in deprecated:
            found = soup.find_all(tag)
            if found:
                bugs.append({
                    "type": "warning",
                    "message": f"Deprecated <{tag}> element found ({len(found)} occurrence(s))"
                })
        
        return bugs if len(bugs) > 1 else [{"type": "info", "message": "No major HTML issues detected"}]
    
    def _has_doctype(self, html: str) -> bool:
        """Check for DOCTYPE declaration"""
        return bool(re.search(r'^\s*<!DOCTYPE\s+html', html, re.IGNORECASE))
    
    def _find_duplicate_ids(self, soup: BeautifulSoup) -> List[str]:
        """Find duplicate ID attributes"""
        id_counts = {}
        for element in soup.find_all(id=True):
            element_id = element.get('id')
            id_counts[element_id] = id_counts.get(element_id, 0) + 1
        return [id_val for id_val, count in id_counts.items() if count > 1]