# ScrapeFlow Studio | Web Scraper & PostgreSQL CRUD System

A clean, beginner-friendly Python web scraping and database application. It scrapes data from websites (both dynamic and static), stores the data into a live **PostgreSQL** database using `psycopg2` via secure parameterized SQL queries, provides REST APIs for full **CRUD** and **Database Schema Introspection**, features a modern dark-mode Frontend UI, and includes a standalone **CSV Export script** using Python's standard `csv` module.

---

## 1. Project Directory Structure

```text
universal-scraper-postgres/
├── .env                      # Active live PostgreSQL database configuration
├── requirements.txt          # Python dependencies
├── run_server.py             # One-click launcher for the FastAPI server
├── export_to_csv.py          # Standalone CSV export script using Python's 'csv' module
├── test_suite.py             # Automated verification test suite
├── README.md                 # Project documentation & explanations
├── PRESENTATION_GUIDE.md     # Presentation script & Tutor Q&A cheat sheet
│
├── static/                   # Frontend Web Interface
│   ├── index.html            # Clean HTML5 structure
│   ├── css/styles.css        # Modern dark-mode styling
│   └── js/app.js             # Beginner-friendly vanilla JavaScript (async/await + fetch)
│
├── scraper/                  # Web Scraping Engine
│   ├── dynamic_detector.py   # Checks if a website is dynamic or static
│   └── universal_scraper.py  # Scrapes data using requests and BeautifulSoup
│
├── database/                 # PostgreSQL Database Operations
│   ├── connection.py         # Connects to PostgreSQL using psycopg2 (with SQLite fallback)
│   ├── repository.py         # Clean parameterized SQL queries for CRUD & Schema
│   └── schema.sql            # Table schema definition
│
└── api/
    └── main.py               # Clear, unified FastAPI REST API endpoints
```

---

## 2. Core Features & Assignment Requirements

| Requirement | How It Is Implemented |
| :--- | :--- |
| **1. Identify Dynamic Websites** | Uses `scraper/dynamic_detector.py` to inspect HTML for `<noscript>` tags, empty SPA containers (`#root`), and inline JavaScript data variables. |
| **2. Universal Web Scraping** | Uses `scraper/universal_scraper.py` with `requests` and `BeautifulSoup` to extract structured data from dynamic quotes, book catalogs, tables, or general articles. |
| **3. Live PostgreSQL Database** | Connects to PostgreSQL using `psycopg2` in `database/connection.py`. Executes parameterized SQL queries in `database/repository.py` to prevent SQL injection. |
| **4. RESTful CRUD APIs** | FastAPI endpoints in `api/main.py` allowing users to **Create**, **Read** (with search/pagination), **Update**, and **Delete** records. |
| **5. Database Schema API** | Endpoint `/api/schema` queries PostgreSQL's `information_schema.columns` to dynamically inspect table fields and data types. |
| **6. Standalone CSV Script** | `export_to_csv.py` uses Python's standard `csv` module to read from PostgreSQL and write an Excel-ready CSV file with UTF-8 BOM encoding. |
| **7. Interactive Web Dashboard** | Modern dark-mode UI with presets, dynamic detection visualizer, live scraping cards, CRUD record manager, and schema explorer. |
| **8. Automated Verification** | `test_suite.py` tests all requirements in 7 automated steps with 100% pass rates. |

---

## 3. How to Identify a Dynamic Website

### Concept
* **Static Website**: The server returns complete, pre-rendered HTML. All the text and images exist directly in the initial HTTP response.
* **Dynamic Website**: The server returns a minimal HTML skeleton (like `<div id="root"></div>`) alongside JavaScript files. The browser executes the JavaScript, which fetches data from APIs and injects elements into the page at runtime.

### Manual Verification (The "Disable JavaScript" Test in Chrome)
1. Open the target website (e.g. `https://quotes.toscrape.com/js/`).
2. Press `F12` (or `Ctrl + Shift + I`) to open Chrome Developer Tools.
3. Press `Ctrl + Shift + P`, type **`Disable JavaScript`**, and press Enter.
4. Refresh the webpage (`Ctrl + R` or `F5`).
5. **Result**: The quotes completely vanish! Because the browser can't run JavaScript, the content cannot be rendered. This proves the site is dynamic.

### Automated Python Detection (`scraper/dynamic_detector.py`)
Our script sends a GET request and checks for three key signals:
1. `<noscript>` tags warning the user that JavaScript must be enabled.
2. Empty SPA root containers like `<div id="root"></div>` or `<div id="app"></div>`.
3. Client-side inline data variables (e.g. `var data = [...]`).

---

## 4. How to Run the Project

### 1. Launch the Server
```bash
python run_server.py
```

### 2. Open the Web Application
* 🌐 **Web Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* 📖 **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 🩺 **Database Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
* 📥 **One-Click CSV Download**: [http://127.0.0.1:8000/api/export/csv](http://127.0.0.1:8000/api/export/csv)

### 3. Run the Automated Test Suite
```bash
python test_suite.py
```
This runs 7 automated tests validating the database, dynamic detection, web scraping, CRUD, schema inspection, and CSV export.

### 4. Run the Standalone CSV Export Script
```bash
python export_to_csv.py
```
Generates `scraped_data_export.csv` directly from PostgreSQL using Python's standard `csv` module.
