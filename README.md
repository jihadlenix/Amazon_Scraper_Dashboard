# 🛒 Amazon Product Scraper Dashboard

A full-stack application that scrapes **public Amazon search results**, stores them in a **SQLite database**, and visualizes the data in a **React dashboard** with filters, and CSV export.

Built using **FastAPI**, **Selenium**, **BeautifulSoup**, and **React (Vite + TypeScript)**.

---

## Features

### Scraper
- Scrapes **public Amazon search pages** (no login or private endpoints).
- Extracts:
  - Product title  
  - Price (if available)  
  - Rating (if available)  
  - Product URL  
  - Image URL  
- Handles multiple pages with delays to avoid rate-limiting.
- Deduplicates results and saves into a local SQLite database.

### Backend (FastAPI)
- REST API endpoints for scraping and fetching stored data.
- Supports filtering by product name, rating, and price.
- Automatically tracks **price history** for repeated scrapes.
- CSV export endpoint.

### Frontend (React + Vite)
- Simple interactive dashboard:
  - “Scrape New Data” button (keyword or search URL)
  - Filters by name, min rating, and max price
  - Data table with product images, titles, prices, ratings, and direct Amazon links
  - CSV export option
- Loading and toast notifications.

## Backend Setup (FastAPI)

### 1. Create and activate a virtual environment
```bash
cd scraper_spec_backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # macOS/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the API server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Access
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

##  API Endpoints

### `POST /scrape`
Triggers scraping for a keyword or URL.

**Example (keyword):**
```json
{
  "keyword": "wireless headphones",
  "domain": "amazon.com",
  "max_pages": 1,
  "delay_lo": 2.5,
  "delay_hi": 5.0
}
```

**Example (URL):**
```json
{
  "search_url": "https://www.amazon.com/s?k=wireless+headphones",
  "max_pages": 1
}
```

**Response:**
```json
{"fetched": 40, "inserted_or_updated": 40}
```

---

### `GET /products`
Fetch products with optional filters and pagination.

**Query Parameters:**
- `q`: string (name contains)
- `min_rating`: float
- `max_price`: float
- `page`: int (default 1)
- `page_size`: int (default 50)
- `order_by`: price | rating | created_at | updated_at | title
- `order`: asc | desc

---

### `GET /products.csv`
Exports filtered products to CSV.

---

### `GET /history/{asin}`
Returns the price history for a specific product (if scraped multiple times).

---

##  Frontend Setup (React Dashboard)

### 1. Install dependencies
```bash
cd scraper_frontend_react
npm install
```

### 2. Configure API URL
In `.env`
```
VITE_API_BASE=http://127.0.0.1:8000
```

### 3. Run the dashboard
```bash
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

### 4. Deployment link
https://amazon-scraper-dashboard.onrender.com/
https://amazon-scraper-dashboard-7c7t-git-main-jihads-projects-95bc20fd.vercel.app/