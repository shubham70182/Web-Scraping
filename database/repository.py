"""
Database Repository Module.

Handles all SQL operations on the 'scraped_items' table:
- Inserting scraped records
- CRUD operations (Create, Read, Update, Delete)
- Database schema inspection (information_schema.columns)

Security Note: All queries use parameterized placeholders (%s or ?) to completely
prevent SQL injection attacks.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from database.connection import get_connection

def _format_row(row) -> Dict[str, Any]:
    """Helper function to turn a database row into a standard Python dictionary."""
    if not row:
        return None
    data = dict(row)
    # Ensure date objects are converted to strings so FastAPI can send them as JSON
    if data.get("scraped_at"):
        data["scraped_at"] = str(data["scraped_at"])
    if data.get("updated_at"):
        data["updated_at"] = str(data["updated_at"])
    # If extra_data is a JSON string, parse it into a dict
    if isinstance(data.get("extra_data"), str):
        try:
            data["extra_data"] = json.loads(data["extra_data"])
        except Exception:
            data["extra_data"] = {}
    return data

def insert_scraped_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Inserts a list of scraped items into the database.
    Uses parameterized SQL to prevent SQL injection.
    """
    if not items:
        return []

    conn, cur, engine = get_connection()
    inserted_records = []

    try:
        for item in items:
            source_url = item.get("source_url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            content = item.get("content", "")
            item_type = item.get("item_type", "generic")
            extra_data = item.get("extra_data", {})
            extra_json = json.dumps(extra_data)

            if engine == "postgresql":
                sql = """
                    INSERT INTO scraped_items (source_url, title, description, content, item_type, extra_data)
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id, source_url, title, description, content, item_type, extra_data, scraped_at, updated_at;
                """
                cur.execute(sql, (source_url, title, description, content, item_type, extra_json))
                inserted_records.append(_format_row(cur.fetchone()))
            else:
                sql = """
                    INSERT INTO scraped_items (source_url, title, description, content, item_type, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?);
                """
                cur.execute(sql, (source_url, title, description, content, item_type, extra_json))
                item_id = cur.lastrowid
                cur.execute("SELECT * FROM scraped_items WHERE id = ?", (item_id,))
                inserted_records.append(_format_row(cur.fetchone()))

        conn.commit()
    finally:
        cur.close()
        conn.close()

    return inserted_records

def get_items(limit: int = 50, offset: int = 0, search: Optional[str] = None,
              source_url: Optional[str] = None, item_type: Optional[str] = None) -> Tuple[List[Dict[str, Any]], int]:
    """
    Retrieves stored records with optional search, filtering, and pagination.
    """
    conn, cur, engine = get_connection()
    try:
        where_clauses = []
        params = []
        placeholder = "%s" if engine == "postgresql" else "?"

        if search:
            # Search title or description
            pattern = f"%{search}%"
            op = "ILIKE" if engine == "postgresql" else "LIKE"
            where_clauses.append(f"(title {op} {placeholder} OR description {op} {placeholder})")
            params.extend([pattern, pattern])

        if source_url:
            where_clauses.append(f"source_url {placeholder}")
            params.append(f"%{source_url}%")

        if item_type:
            where_clauses.append(f"item_type = {placeholder}")
            params.append(item_type)

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Count total matching rows
        count_sql = f"SELECT COUNT(*) as total FROM scraped_items {where_sql};"
        cur.execute(count_sql, tuple(params))
        total_row = cur.fetchone()
        total_count = total_row["total"] if isinstance(total_row, dict) else total_row[0]

        # Fetch the paginated rows
        fetch_sql = f"""
            SELECT id, source_url, title, description, content, item_type, extra_data, scraped_at, updated_at
            FROM scraped_items
            {where_sql}
            ORDER BY id DESC
            LIMIT {placeholder} OFFSET {placeholder};
        """
        fetch_params = params + [limit, offset]
        cur.execute(fetch_sql, tuple(fetch_params))
        rows = cur.fetchall()

        items = [_format_row(r) for r in rows]
        return items, total_count
    finally:
        cur.close()
        conn.close()

def get_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single item by its primary key ID."""
    conn, cur, engine = get_connection()
    try:
        placeholder = "%s" if engine == "postgresql" else "?"
        cur.execute(f"SELECT * FROM scraped_items WHERE id = {placeholder};", (item_id,))
        row = cur.fetchone()
        return _format_row(row)
    finally:
        cur.close()
        conn.close()

def create_item(source_url: str, title: str, description: str = "", item_type: str = "manual") -> Dict[str, Any]:
    """Manually creates a new record in the database."""
    items = [{
        "source_url": source_url,
        "title": title,
        "description": description,
        "content": "",
        "item_type": item_type,
        "extra_data": {}
    }]
    results = insert_scraped_items(items)
    return results[0] if results else None

def update_item(item_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Updates an existing record's title and description."""
    conn, cur, engine = get_connection()
    try:
        placeholder = "%s" if engine == "postgresql" else "?"
        sql = f"""
            UPDATE scraped_items
            SET title = COALESCE({placeholder}, title),
                description = COALESCE({placeholder}, description),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = {placeholder};
        """
        cur.execute(sql, (title, description, item_id))
        conn.commit()
        cur.execute(f"SELECT * FROM scraped_items WHERE id = {placeholder};", (item_id,))
        return _format_row(cur.fetchone())
    finally:
        cur.close()
        conn.close()

def delete_item(item_id: int) -> bool:
    """Deletes a record from the database by ID."""
    conn, cur, engine = get_connection()
    try:
        placeholder = "%s" if engine == "postgresql" else "?"
        cur.execute(f"DELETE FROM scraped_items WHERE id = {placeholder};", (item_id,))
        conn.commit()
        # rowcount indicates how many rows were deleted
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()

def get_table_schema() -> List[Dict[str, Any]]:
    """
    Introspects the database schema.
    For PostgreSQL, queries 'information_schema.columns'.
    For SQLite, queries 'PRAGMA table_info'.
    """
    conn, cur, engine = get_connection()
    columns = []
    try:
        if engine == "postgresql":
            sql = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'scraped_items'
                ORDER BY ordinal_position;
            """
            cur.execute(sql)
            for row in cur.fetchall():
                columns.append({
                    "column_name": row["column_name"],
                    "data_type": row["data_type"],
                    "is_nullable": row["is_nullable"],
                    "default_value": row["column_default"]
                })
        else:
            cur.execute("PRAGMA table_info(scraped_items);")
            for row in cur.fetchall():
                columns.append({
                    "column_name": row["name"],
                    "data_type": row["type"],
                    "is_nullable": "NO" if row["notnull"] else "YES",
                    "default_value": row["dflt_value"]
                })
        return columns
    finally:
        cur.close()
        conn.close()
