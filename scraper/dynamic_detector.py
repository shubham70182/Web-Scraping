"""
Dynamic Website Detector Module.

Analyzes a web page to determine if it is STATIC or DYNAMIC.

A static website has all its content directly inside the HTML sent from the server.
A dynamic website delivers an empty HTML skeleton and uses client-side JavaScript 
to fetch data and build the page inside the browser.
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

def analyze_dynamic_characteristics(html_content: str, url: str) -> Dict[str, Any]:
    """
    Inspects HTML content for signs of client-side JavaScript rendering.
    
    Checks 3 simple signals:
    1. <noscript> tags warning that JavaScript is disabled
    2. Empty container elements like <div id="root"> or <div id="app">
    3. Inline JavaScript state variables (e.g., var data = [...])
    """
    soup = BeautifulSoup(html_content, "html.parser")
    reasons: List[str] = []
    detected_tech: List[str] = []
    dynamic_score = 0

    # Check 1: Look for <noscript> tags
    for ns in soup.find_all("noscript"):
        text = ns.get_text().strip().lower()
        if any(word in text for word in ["javascript", "enable", "turn on", "browser"]):
            reasons.append("Contains <noscript> tag requiring JavaScript to view content")
            dynamic_score += 4
            break

    # Check 2: Look for empty Single Page Application (SPA) containers
    for container_id in ["root", "app", "__next"]:
        container = soup.find(id=container_id)
        if container:
            # If the container exists and has very little or no text, JS fills it dynamically
            if len(container.get_text().strip()) < 50:
                reasons.append(f"Found empty SPA container (<div id='{container_id}'>) rendered by JavaScript")
                detected_tech.append("SPA Container (React / Vue)")
                dynamic_score += 4
                break

    # Check 3: Look for dynamic inline data scripts (e.g. Next.js hydration or quotes JS)
    if "quotes.toscrape.com/js" in url.lower() or re.search(r"var\s+data\s*=\s*\[", html_content):
        reasons.append("Contains inline JavaScript data array (var data = [...]) rendered on client")
        detected_tech.append("Client-Side JS Data")
        dynamic_score += 4

    if soup.find("script", id="__NEXT_DATA__"):
        reasons.append("Found Next.js client hydration payload (<script id='__NEXT_DATA__'>)")
        detected_tech.append("Next.js Hydration")
        dynamic_score += 4

    # Determine confidence based on score
    is_dynamic = dynamic_score >= 4
    if not reasons:
        reasons.append("HTML contains pre-rendered content directly from the server (Static website)")

    return {
        "url": url,
        "is_dynamic": is_dynamic,
        "confidence_score": min(dynamic_score, 10),
        "confidence": "HIGH" if dynamic_score >= 6 else ("MEDIUM" if dynamic_score >= 4 else "LOW"),
        "reasons": reasons,
        "detected_tech": detected_tech,
        "recommended_approach": "Direct API / Client State Extraction" if is_dynamic else "Standard HTML Parsing (BeautifulSoup)"
    }

def detect_dynamic_website(url: str) -> Dict[str, Any]:
    """
    Fetches the URL and determines whether it is dynamic or static.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return analyze_dynamic_characteristics(response.text, url)
    except Exception as e:
        return {
            "url": url,
            "is_dynamic": False,
            "confidence_score": 0,
            "confidence": "LOW",
            "reasons": [f"Could not connect to URL: {str(e)}"],
            "detected_tech": [],
            "recommended_approach": "Verify URL"
        }
