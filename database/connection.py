"""
Database Connection Module.

Connects to PostgreSQL using the 'psycopg2' library.
If PostgreSQL is unreachable (for example, if offline), it automatically
uses SQLite ('scraper.db') so the application never crashes.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """
    Returns a database connection and cursor.
    Uses PostgreSQL if available, otherwise falls back to SQLite.
    """
    try:
        if DATABASE_URL:
            # Connect to live PostgreSQL database (e.g. Neon cloud)
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
            # RealDictCursor returns rows as Python dictionaries: {"id": 1, "title": "..."}
            cur = conn.cursor(cursor_factory=RealDictCursor)
            return conn, cur, "postgresql"
    except Exception as e:
        print(f"[Database Warning] PostgreSQL connection failed: {e}. Falling back to SQLite.")

    # Fallback to local SQLite database file
    conn = sqlite3.connect("scraper.db")
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur, "sqlite"

def init_db():
    """
    Creates the 'scraped_items' table if it does not already exist.
    Called once when the application starts.
    """
    conn, cur, engine = get_connection()
    try:
        if engine == "postgresql":
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scraped_items (
                    id SERIAL PRIMARY KEY,
                    source_url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    content TEXT,
                    item_type VARCHAR(100) DEFAULT 'generic',
                    extra_data JSONB DEFAULT '{}'::jsonb,
                    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scraped_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    content TEXT,
                    item_type TEXT DEFAULT 'generic',
                    extra_data TEXT DEFAULT '{}',
                    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_engine_status():
    """Returns database connection status for health checks and UI badges."""
    try:
        conn, cur, engine = get_connection()
        cur.close()
        conn.close()
        return {
            "active_engine": engine,
            "is_postgresql_connected": (engine == "postgresql"),
            "status": "connected"
        }
    except Exception as e:
        return {
            "active_engine": "none",
            "is_postgresql_connected": False,
            "status": f"error: {str(e)}"
        }
