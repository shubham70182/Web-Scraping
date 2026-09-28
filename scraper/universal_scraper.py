"""
Universal Web Scraper Module.

Scrapes structured data across websites using standard 'requests' and 'BeautifulSoup'.
Extracts quotes, books/products, HTML tables, or general articles & headings.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_text(text: Optional[str]) -> str:
    """Removes extra spaces and newlines from scraped text."""
    if not text:
        return ""
    return " ".join(text.split()).strip()

def scrape_quotes_js(html: str, url: str) -> List[Dict[str, Any]]:
    """
    Extracts quotes from dynamic JavaScript pages like quotes.toscrape.com/js/.
    These pages store their data inside an inline script: var data = [...];
    """
    match = re.search(r"var\s+data\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not match:
        return []

    try:
        raw_quotes = json.loads(match.group(1))
        results = []
        for q in raw_quotes:
            text = q.get("text", "").strip("“”\"' ")
            author = q.get("author", {}).get("name", "Unknown") if isinstance(q.get("author"), dict) else str(q.get("author", "Unknown"))
            tags = q.get("tags", [])
            tag_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            
            results.append({
                "source_url": url,
                "title": f"Quote by {author}",
                "description": text,
                "content": f"Tags: {tag_str}",
                "item_type": "quote",
                "extra_data": {"author": author, "tags": tags}
            })
        return results
    except Exception:
        return []

def scrape_quotes_html(soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
    """Extracts quotes from standard HTML pages."""
    quote_elements = soup.find_all("div", class_="quote")
    if not quote_elements:
        return []

    results = []
    for el in quote_elements:
        text_el = el.find(class_="text")
        author_el = el.find(class_="author")
        text = text_el.get_text().strip("“”\"' ") if text_el else ""
        author = author_el.get_text().strip() if author_el else "Unknown"

        tags = [t.get_text().strip() for t in el.find_all(class_="tag")]
        tag_str = ", ".join(tags) if tags else ""

        results.append({
            "source_url": url,
            "title": f"Quote by {author}",
            "description": text,
            "content": f"Tags: {tag_str}",
            "item_type": "quote",
            "extra_data": {"author": author, "tags": tags}
        })
    return results

def scrape_books_or_products(soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
    """Extracts books or products (e.g. books.toscrape.com)."""
    product_elements = soup.find_all("article", class_="product_pod")
    if not product_elements:
        product_elements = soup.find_all(class_=re.compile(r"product|card|item", re.I))

    results = []
    for p in product_elements[:30]:
        title_tag = p.find(["h3", "h2", "h4"])
        link_tag = p.find("a")
        title = ""
        if title_tag:
            title = title_tag.get_text().strip()
            if link_tag and link_tag.get("title"):
                title = link_tag.get("title").strip()
        elif link_tag and link_tag.get("title"):
            title = link_tag.get("title").strip()

        price_tag = p.find(class_="price_color")
        if not price_tag:
            price_tag = p.find(class_=re.compile(r"price", re.I))
        price = clean_text(price_tag.get_text()) if price_tag else "N/A"

        if title and len(title) > 2:
            results.append({
                "source_url": url,
                "title": title,
                "description": f"Price: {price}",
                "content": f"Product listed on {url}",
                "item_type": "product",
                "extra_data": {"price": price}
            })
    return results

def scrape_tables(soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
    """Extracts rows from HTML tables."""
    tables = soup.find_all("table")
    results = []

    for table in tables:
        headers = [th.get_text().strip() for th in table.find_all("th")]
        rows = table.find_all("tr")
        for row in rows:
            cells = [td.get_text().strip() for td in row.find_all("td")]
            if cells:
                row_title = cells[0] if cells else "Table Row"
                row_desc = " | ".join(cells[1:]) if len(cells) > 1 else ""
                results.append({
                    "source_url": url,
                    "title": row_title,
                    "description": row_desc,
                    "content": " | ".join(f"{h}: {c}" for h, c in zip(headers, cells)) if headers else row_desc,
                    "item_type": "table_row",
                    "extra_data": {"row": cells}
                })
    return results

def scrape_generic_content(soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
    """Fallback: extracts headings and paragraphs from articles or general pages."""
    results = []
    # Find all major headings on the page
    headings = soup.find_all(["h1", "h2", "h3"])
    
    for h in headings[:25]:
        title = clean_text(h.get_text())
        if len(title) < 3:
            continue
        
        # Look for the immediate next paragraph
        next_p = h.find_next_sibling("p")
        desc = clean_text(next_p.get_text()) if next_p else ""
        
        results.append({
            "source_url": url,
            "title": title,
            "description": desc,
            "content": f"Section extracted from {url}",
            "item_type": "article_section",
            "extra_data": {}
        })
    return results

def scrape_website(url: str, max_items: int = 50) -> Dict[str, Any]:
    """
    Main universal scraping function.
    Downloads the page and selects the best extraction strategy.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        items = []
        strategy = "generic_content"

        # 1. Check for dynamic JavaScript quotes (e.g. quotes.toscrape.com/js/)
        if "quotes.toscrape.com/js" in url.lower() or "var data = [" in html:
            items = scrape_quotes_js(html, url)
            if items:
                strategy = "inline_javascript_state"

        # 2. Check for standard HTML quotes
        if not items:
            items = scrape_quotes_html(soup, url)
            if items:
                strategy = "html_quotes"

        # 3. Check for books / products
        if not items:
            items = scrape_books_or_products(soup, url)
            if items:
                strategy = "product_cards"

        # 4. Check for tables
        if not items:
            items = scrape_tables(soup, url)
            if items:
                strategy = "html_tables"

        # 5. Fallback to general headings and paragraphs
        if not items:
            items = scrape_generic_content(soup, url)
            strategy = "document_headings"

        return {
            "source_url": url,
            "strategy_used": strategy,
            "total_items": len(items[:max_items]),
            "items": items[:max_items]
        }
    except Exception as e:
        return {
            "source_url": url,
            "strategy_used": "error",
            "total_items": 0,
            "items": [],
            "error": str(e)
        }
