# Web Scraper & PostgreSQL CRUD System

An end-to-end Python web scraping and data management system. It scrapes structured data from both static and dynamic websites, stores records into a live **PostgreSQL** database using secure parameterized queries, exposes a full **RESTful CRUD API** with database schema introspection via **FastAPI**, and provides a modern web dashboard along with a standalone **CSV export script**.

📌 Features:

- **Universal Web Scraper**: Extracts structured content (quotes, books, tables, articles) using `requests` and `BeautifulSoup4`.
- **Dynamic Site Detection**: Automatically detects whether a site requires client-side JavaScript execution (SPAs, React/Vue containers) or is server-rendered static HTML.
- **PostgreSQL Database Storage**: Uses `psycopg2` with parameterized SQL queries (`%s`) to prevent SQL injection vulnerabilities.
- **RESTful CRUD API**: Built with FastAPI to Create, Read (with search and pagination), Update, and Delete database records.
- **Schema Introspection**: Dynamic endpoint `/api/schema` querying PostgreSQL's `information_schema.columns`.
- **Standalone CSV Export**: Independent script (`export_to_csv.py`) using Python's standard `csv` module with UTF-8 BOM encoding for seamless Excel compatibility.
- **Interactive Web Dashboard**: Modern UI with dynamic site analysis, live scraping, CRUD data manager, and one-click CSV download.
- **Automated Verification**: End-to-end test suite (`test_suite.py`) validating all pipeline components.

⚙️ Prerequisites & Setup:

1. Requirements:
Python 3.8 or higher
PostgreSQL database (local or hosted instance)

2. Installation
 Clone or navigate to the project directory:
 cd universal-scraper-postgres

 Create and activate a virtual environment (optional but recommended):
 # Windows
 python -m venv venv
 venv\Scripts\activate
 # macOS / Linux
 python3 -m venv venv
 source venv/bin/activate 
 
 Install dependencies:
 pip install -r requirements.txt

How to Run
1. Start the Web Server & Dashboard:
python run_server.py

🌐 Web Dashboard: http://localhost:8000/
📖 Interactive API Docs (Swagger UI): http://localhost:8000/docs
🩺 Health Check: http://localhost:8000/api/health

Run the Standalone CSV Export Script:
python export_to_csv.py

Queries PostgreSQL and outputs scraped_data_export.csv directly in the project folder.

Run the Automated Test Suite:
python test_suite.py

Executes automated tests validating database connectivity, dynamic site detection, web scraping, CRUD operations, schema introspection, and CSV generation.
