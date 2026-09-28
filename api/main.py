"""
FastAPI Application Entry Point.

Provides simple, clear RESTful APIs for:
1. Dynamic Website Detection: GET /api/detect-dynamic
2. Web Scraping & Database Insertion: POST /api/scrape
3. CRUD Operations: GET, POST, PUT, DELETE /api/items
4. Database Schema Inspection: GET /api/schema
5. CSV Export Download: GET /api/export/csv
6. Frontend Web Dashboard: GET /
"""

import os
import io
import csv
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from database.connection import init_db, get_engine_status
from database.repository import (
    insert_scraped_items,
    get_items,
    get_item_by_id,
    create_item,
    update_item,
    delete_item,
    get_table_schema
)
from scraper.dynamic_detector import detect_dynamic_website
from scraper.universal_scraper import scrape_website

# Initialize FastAPI application
app = FastAPI(
    title="Universal Web Scraper & PostgreSQL API",
    description="A simple, clear REST API for dynamic web scraping, PostgreSQL storage, and CRUD operations.",
    version="1.0.0"
)

# Enable CORS so browser can make requests without cross-origin blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files folder (HTML, CSS, JS)
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Automatically initialize database table when server starts
@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Data Models (Request validation) ---

class ScrapeRequest(BaseModel):
    url: str
    max_items: Optional[int] = 50

class ItemCreateRequest(BaseModel):
    source_url: str
    title: str
    description: Optional[str] = ""
    item_type: Optional[str] = "manual"

class ItemUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

# --- API Endpoints ---

@app.get("/", summary="Frontend Web Dashboard")
def serve_frontend():
    """Serves the frontend index.html web dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found. Check Swagger docs at /docs"}

@app.get("/api/health", summary="Health Check & DB Status")
def health_check():
    """Returns database connection status."""
    return {
        "status": "healthy",
        "database": get_engine_status()
    }

@app.get("/api/detect-dynamic", summary="Detect if Website is Dynamic or Static")
def detect_dynamic_endpoint(url: str = Query(..., description="Target website URL")):
    """
    Checks if a target website relies on JavaScript to render its content.
    """
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    return detect_dynamic_website(url)

@app.post("/api/scrape", summary="Scrape Website and Save to PostgreSQL")
def scrape_and_store_endpoint(request: ScrapeRequest):
    """
    1. Downloads and parses the target URL using requests and BeautifulSoup.
    2. Inserts the scraped records directly into PostgreSQL using parameterized SQL.
    """
    url = request.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    # Step 1: Scrape the website
    scrape_result = scrape_website(url, max_items=request.max_items or 50)
    scraped_items = scrape_result.get("items", [])

    if not scraped_items:
        return {
            "success": False,
            "message": f"No items could be extracted from {url}. Strategy: {scrape_result.get('strategy_used')}",
            "strategy_used": scrape_result.get("strategy_used"),
            "count": 0,
            "items": []
        }

    # Step 2: Store in PostgreSQL
    saved_items = insert_scraped_items(scraped_items)

    return {
        "success": True,
        "message": f"Successfully scraped and stored {len(saved_items)} items in PostgreSQL.",
        "strategy_used": scrape_result.get("strategy_used"),
        "count": len(saved_items),
        "items": saved_items
    }

# --- CRUD Endpoints ---

@app.get("/api/items", summary="Read Items from Database")
def read_items_endpoint(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search term for title or description"),
    source_url: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None)
):
    """Retrieves stored records with optional search and pagination."""
    items, total = get_items(limit=limit, offset=offset, search=search, source_url=source_url, item_type=item_type)
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/items/{item_id}", summary="Get Single Item by ID")
def get_single_item_endpoint(item_id: int):
    """Fetches a specific record by its primary key ID."""
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
    return item

@app.post("/api/items", summary="Create New Record Manually")
def create_item_endpoint(item: ItemCreateRequest):
    """Manually inserts a new record into the database."""
    created = create_item(
        source_url=item.source_url,
        title=item.title,
        description=item.description,
        item_type=item.item_type
    )
    return created

@app.put("/api/items/{item_id}", summary="Update Existing Record")
def update_item_endpoint(item_id: int, item: ItemUpdateRequest):
    """Updates an existing record's title or description in the database."""
    updated = update_item(item_id, title=item.title, description=item.description)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
    return updated

@app.delete("/api/items/{item_id}", summary="Delete Record by ID")
def delete_item_endpoint(item_id: int):
    """Deletes a record from the database by its ID."""
    success = delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
    return {"success": True, "message": f"Item {item_id} successfully deleted."}

# --- Database Schema Introspection Endpoint ---

@app.get("/api/schema", summary="Inspect Database Schema")
def get_schema_endpoint():
    """
    Introspects table columns and data types from PostgreSQL 'information_schema.columns'.
    """
    columns = get_table_schema()
    return {
        "table_name": "scraped_items",
        "columns": columns
    }

# --- CSV Export Endpoint ---

@app.get("/api/export/csv", summary="Download Scraped Data as CSV")
def export_csv_download(
    search: Optional[str] = None,
    source_url: Optional[str] = None,
    limit: int = 1000
):
    """
    Generates a CSV file on the fly using Python's standard 'csv' module
    and streams it directly to the browser for instant download.
    """
    items, total = get_items(limit=limit, search=search, source_url=source_url)
    
    output = io.StringIO()
    # Write UTF-8 BOM so Microsoft Excel correctly displays special characters
    output.write("\ufeff")
    
    writer = csv.writer(output)
    # Write header row
    writer.writerow(["ID", "Source URL", "Title", "Description", "Item Type", "Scraped At"])
    
    for row in items:
        writer.writerow([
            row.get("id"),
            row.get("source_url"),
            row.get("title"),
            row.get("description"),
            row.get("item_type"),
            row.get("scraped_at")
        ])
        
    csv_content = output.getvalue()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=scraped_data_export.csv"
        }
    )
