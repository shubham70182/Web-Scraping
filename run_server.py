"""
Server Launcher Script.
Starts the FastAPI application using Uvicorn with auto-reload.
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("API_HOST", "127.0.0.1")
PORT = int(os.getenv("API_PORT", "8000"))

def main():
    print("=" * 65)
    print("  UNIVERSAL WEB SCRAPER & POSTGRESQL API")
    print("=" * 65)
    print(f"  Interactive Swagger Docs:  http://{HOST}:{PORT}/docs")
    print(f"  Alternative ReDoc:         http://{HOST}:{PORT}/redoc")
    print(f"  Health & Engine Status:    http://{HOST}:{PORT}/api/health")
    print(f"  Direct CSV Export:         http://{HOST}:{PORT}/api/export/csv")
    print("=" * 65)
    print("  Press Ctrl+C to terminate the server.\n")

    uvicorn.run("api.main:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()
