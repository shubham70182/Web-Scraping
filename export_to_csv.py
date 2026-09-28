"""
Standalone CSV Generation Script.

Reads records from the PostgreSQL database and exports them to a clean CSV file
using Python's built-in 'csv' module.

Usage:
    python export_to_csv.py
"""

import os
import csv
from database.connection import init_db
from database.repository import get_items

def export_scraped_data_to_csv(filename: str = "scraped_data_export.csv", limit: int = 1000) -> str:
    """
    Fetches records from PostgreSQL and writes them to a CSV file.
    """
    # 1. Initialize database connection
    init_db()

    print("\n[CSV Exporter] Connecting to database and fetching records...")
    items, total_count = get_items(limit=limit)

    if not items:
        print("[CSV Exporter] No records found in database to export.")
        return None

    print(f"[CSV Exporter] Found {len(items)} record(s). Writing to CSV...")

    # 2. Define the column headers for the CSV
    headers = ["ID", "Source URL", "Title", "Description", "Item Type", "Scraped At"]

    # 3. Open file with 'utf-8-sig' (includes BOM so Microsoft Excel opens it cleanly)
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(headers)

        # Write each record row
        for item in items:
            writer.writerow([
                item.get("id"),
                item.get("source_url"),
                item.get("title"),
                item.get("description"),
                item.get("item_type"),
                item.get("scraped_at")
            ])

    abs_path = os.path.abspath(filename)
    print(f"[CSV Exporter] SUCCESS! File saved to: {abs_path}\n")
    return abs_path

if __name__ == "__main__":
    export_scraped_data_to_csv()
