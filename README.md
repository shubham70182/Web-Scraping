# Web Scraper & PostgreSQL CRUD System

An end-to-end Python web scraping and data management system. It scrapes structured data from both static and dynamic websites, stores records into a live **PostgreSQL** database using secure parameterized queries, exposes a full **RESTful CRUD API** with database schema introspection via **FastAPI**, and provides a modern web dashboard along with a standalone **CSV export script**.

---

## 📌 Features

- **Universal Web Scraper**: Extracts structured content (quotes, books, tables, articles) using `requests` and `BeautifulSoup4`.
- **Dynamic Site Detection**: Automatically detects whether a site requires client-side JavaScript execution (SPAs, React/Vue containers) or is server-rendered static HTML.
- **PostgreSQL Database Storage**: Uses `psycopg2` with parameterized SQL queries (`%s`) to prevent SQL injection vulnerabilities.
- **RESTful CRUD API**: Built with FastAPI to Create, Read (with search and pagination), Update, and Delete database records.
- **Schema Introspection**: Dynamic endpoint `/api/schema` querying PostgreSQL's `information_schema.columns`.
- **Standalone CSV Export**: Independent script (`export_to_csv.py`) using Python's standard `csv` module with UTF-8 BOM encoding for seamless Excel compatibility.
- **Interactive Web Dashboard**: Modern UI with dynamic site analysis, live scraping, CRUD data manager, and one-click CSV download.
- **Automated Verification**: End-to-end test suite (`test_suite.py`) validating all pipeline components.

---

## 📂 Project Directory Structure

```text
universal-scraper-postgres/
├── .env                      # Database credentials and environment variables
├── .env.example              # Sample environment template
├── requirements.txt          # Python dependencies
├── run_server.py             # One-click launcher for the FastAPI server
├── export_to_csv.py          # Standalone script to export DB records to CSV
├── test_suite.py             # Automated test suite
├── README.md                 # Project documentation
│
├── api/
│   └── main.py               # FastAPI REST endpoints & static file serving
│
├── database/
│   ├── connection.py         # Database connection manager (psycopg2)
│   ├── repository.py         # Parameterized SQL queries (CRUD & Schema)
│   └── schema.sql            # Table schema definition
│
├── scraper/
│   ├── dynamic_detector.py   # Detection logic for dynamic / SPA websites
│   └── universal_scraper.py  # Content extraction engine (BeautifulSoup)
│
└── static/                   # Frontend Web Dashboard
    ├── index.html            # Dashboard markup
    ├── css/styles.css        # Clean dark-mode stylesheet
    └── js/app.js             # Vanilla JavaScript frontend logic
```

---

## ⚙️ Prerequisites & Setup

### 1. Requirements
- Python 3.8 or higher
- PostgreSQL database (local or hosted instance)

### 2. Installation

1. **Clone or open the project folder:**
   ```bash
   cd universal-scraper-postgres
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create or edit the `.env` file in the project root:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

---

## 🚀 How to Run

### 1. Start the Web Server & Dashboard
```bash
python run_server.py
```
- 🌐 **Web Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- 📖 **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 2. Run the Standalone CSV Export Script
```bash
python export_to_csv.py
```
Queries PostgreSQL and generates `scraped_data_export.csv` directly in the project folder.

### 3. Run the Automated Test Suite
```bash
python test_suite.py
```
Executes automated tests validating database connectivity, dynamic site detection, web scraping, CRUD operations, schema introspection, and CSV generation.

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the web dashboard (`index.html`) |
| `GET` | `/api/health` | Returns server & database connection status |
| `GET` | `/api/detect-dynamic` | Checks if a target URL is dynamic or static |
| `POST` | `/api/scrape` | Scrapes target URL and stores results in PostgreSQL |
| `GET` | `/api/items` | Lists stored records (supports `search`, `limit`, `offset`) |
| `GET` | `/api/items/{id}` | Fetches a single record by ID |
| `POST` | `/api/items` | Manually creates a new record |
| `PUT` | `/api/items/{id}` | Updates title or description of an existing record |
| `DELETE` | `/api/items/{id}` | Deletes a record by ID |
| `GET` | `/api/schema` | Returns database column names, data types, and constraints |
| `GET` | `/api/export/csv` | Streams database records as a downloadable CSV file |

---

## 💡 How Dynamic Website Detection Works

### Concept
- **Static Website**: The web server returns complete HTML. Content is available immediately in the raw HTTP response.
- **Dynamic Website**: The web server returns a minimal HTML shell (e.g., `<div id="root"></div>`), while client-side JavaScript fetches data and builds the page dynamically in the browser.

### Manual Verification (The Chrome DevTools Test)
1. Open any page (e.g., `https://quotes.toscrape.com/js/`).
2. Open Chrome Developer Tools (`F12` or `Ctrl + Shift + I`).
3. Press `Ctrl + Shift + P`, type `Disable JavaScript`, and hit **Enter**.
4. Refresh the page (`F5`).
5. **Result**: The quotes vanish because content rendering requires JavaScript execution.

### Automated Python Detection (`scraper/dynamic_detector.py`)
Our detection module inspects the initial HTTP response for:
1. `<noscript>` tags stating JavaScript is required.
2. Empty SPA root containers (e.g., `<div id="root">`, `<div id="app">`).
3. Embedded client-side script data payloads (e.g., `var data = [...]`).

---

## 📄 License
This project is open-source and intended for educational and assessment purposes.
