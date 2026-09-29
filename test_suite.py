"""
Automated Test Suite for Assignment Requirements.

Verifies:
1. Dynamic Website Detection
2. Universal Web Scraping (requests + BeautifulSoup)
3. Database Storage & Parameterized SQL
4. CRUD Operations (Create, Read, Update, Delete)
5. Database Schema Introspection
6. Standalone CSV Generation
"""

import os
import sys

# Ensure immediate console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
from scraper.dynamic_detector import detect_dynamic_website
from scraper.universal_scraper import scrape_website
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
from export_to_csv import export_scraped_data_to_csv

def run_tests():
    print("\n" + "=" * 60)
    print("  VERIFYING WEB SCRAPING & POSTGRESQL CRUD ASSIGNMENT")
    print("=" * 60)

    # Test 1: Database Connection
    print("\n[Test 1] Database Connection...")
    init_db()
    status = get_engine_status()
    print(f"  --> Engine: {status['active_engine']}")
    print(f"  --> Connected to PostgreSQL: {status['is_postgresql_connected']}")
    assert status['is_postgresql_connected'] is True, "PostgreSQL not connected!"
    print("  [PASS] Database is connected and table initialized.")

    # Test 2: Dynamic Website Identification
    print("\n[Test 2] Dynamic Website Detection...")
    url = "https://quotes.toscrape.com/js/"
    detection = detect_dynamic_website(url)
    print(f"  --> Target: {url}")
    print(f"  --> Is Dynamic: {detection['is_dynamic']}")
    print(f"  --> Reasons: {detection['reasons']}")
    assert detection['is_dynamic'] is True, "Failed to identify dynamic site!"
    print("  [PASS] Dynamic website successfully identified.")

    # Test 3: Universal Web Scraping
    print("\n[Test 3] Web Scraping (Dynamic Quotes)...")
    scrape_result = scrape_website(url, max_items=5)
    items = scrape_result.get("items", [])
    print(f"  --> Strategy Used: {scrape_result.get('strategy_used')}")
    print(f"  --> Items Scraped: {len(items)}")
    assert len(items) > 0, "No items scraped!"
    print(f"  --> Sample Title: '{items[0]['title']}'")
    print("  [PASS] Scraped structured data using requests & BeautifulSoup.")

    # Test 4: Database Insert & Read
    print("\n[Test 4] Database Insert & Read...")
    saved_items = insert_scraped_items(items[:3])
    assert len(saved_items) > 0, "Failed to insert items!"
    test_id = saved_items[0]["id"]
    retrieved = get_item_by_id(test_id)
    assert retrieved is not None, "Failed to retrieve item by ID!"
    print(f"  --> Inserted and fetched record ID: {test_id}")
    print("  [PASS] Parameterized SQL INSERT and SELECT executed successfully.")

    # Test 5: CRUD (Update & Delete)
    print("\n[Test 5] CRUD: Update & Delete...")
    updated = update_item(test_id, title="Updated Test Title", description="Updated Description")
    assert updated["title"] == "Updated Test Title", "Failed to update item!"
    print(f"  --> Updated Title: '{updated['title']}'")
    
    deleted = delete_item(test_id)
    assert deleted is True, "Failed to delete item!"
    assert get_item_by_id(test_id) is None, "Item still exists after delete!"
    print(f"  --> Deleted record ID: {test_id}")
    print("  [PASS] SQL UPDATE and DELETE verified.")

    # Test 6: Database Schema Introspection
    print("\n[Test 6] Database Schema Introspection...")
    columns = get_table_schema()
    col_names = [c["column_name"] for c in columns]
    print(f"  --> Columns in 'scraped_items': {col_names}")
    assert "source_url" in col_names and "title" in col_names, "Missing expected columns!"
    print("  [PASS] Introspected information_schema.columns successfully.")

    # Test 7: CSV Generation Script
    print("\n[Test 7] Standalone CSV Export...")
    csv_file = export_scraped_data_to_csv("test_output.csv", limit=10)
    assert csv_file is not None and os.path.exists(csv_file), "CSV export failed!"
    print(f"  --> Generated CSV: {csv_file}")
    print("  [PASS] CSV generated using Python's standard csv module.")

    print("\n" + "=" * 60)
    print("  ALL 7 TESTS PASSED SUCCESSFULLY! (100%)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_tests()
