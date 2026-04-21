# ASOS Product Extractor

A web application that extracts product information from ASOS using a Streamlit frontend and FastAPI backend.

## Project Overview

This project consists of two main components that work together to scrape and display ASOS product data:

- **Frontend**: Streamlit web interface (`main.py`) - User-facing application
- **Backend**: FastAPI server (`api.py`) - Product data extraction API

## Files & Components

### 1. **api.py** - FastAPI Backend Server

**Purpose**: Fetches product data from ASOS's official API and returns formatted information.

**How it operates**:
- Runs a FastAPI server on `localhost:8000`
- Accepts GET requests to the `/extract` endpoint with a `product_id` parameter
- Queries ASOS's internal API: `https://www.asos.com/api/product/catalogue/v4/summaries`
- Extracts and formats product data (title, brand, images, URL)
- Returns JSON response with product details

**Key Features**:
- **Error Handling**: Returns 404 if product not found, 500 for request errors
- **Image Processing**: Filters and formats image URLs to be HTTPS-compliant
- **Request Management**: Handles connection errors gracefully using try-except blocks

**How to run**:
```bash
python api.py
```
The server will start on `http://127.0.0.1:8000`

**Endpoint**:
- `GET /extract?product_id={product_id}`
  - Returns: JSON object with `title`, `brand`, `images` (list), and `url`

---

### 2. **main.py** - Streamlit Frontend

**Purpose**: Provides a user-friendly web interface for extracting ASOS product information.

**How it operates**:
1. User enters an ASOS product URL or product ID
2. Extracts the product ID using regex pattern matching (8-10 digit format)
3. Sends the product ID to the FastAPI backend
4. Receives formatted product data and displays it in an interactive table
5. Shows product image, title, brand, product ID, and clickable ASOS link

**Key Features**:
- **URL Parsing**: Regex pattern extracts product IDs from various ASOS URL formats
- **Backend Communication**: Makes HTTP requests to FastAPI endpoint
- **Data Visualization**: Uses Streamlit's `data_editor` with custom column configuration
- **Image Display**: Shows product thumbnail images (320px width format)
- **Error Handling**: Displays user-friendly error messages for invalid input or connection failures

**How to run**:
```bash
streamlit run main.py
```
The app will open at `http://localhost:8501` (default Streamlit port)

---

## Workflow & Data Flow

```
User Input (ASOS URL/Product ID)
         ↓
    Regex Parsing (main.py)
         ↓
    Extract Product ID
         ↓
    HTTP Request to FastAPI (main.py)
         ↓
    ASOS API Query (api.py)
         ↓
    Extract & Format Data (api.py)
         ↓
    Return JSON Response
         ↓
    Display in Streamlit Table (main.py)
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Install Dependencies
```bash
pip install streamlit fastapi uvicorn requests pandas
```

### Running the Application

**Terminal 1 - Start Backend**:
```bash
python api.py
```

**Terminal 2 - Start Frontend**:
```bash
streamlit run main.py
```

Then navigate to `http://localhost:8501` in your browser.

---

## Example Usage

1. Visit the Streamlit app at `http://localhost:8501`
2. Enter an ASOS product URL: `https://www.asos.com/prd/123456789/`
   - Or just the product ID: `123456789`
3. Click "Extract" button
4. View product details in the interactive table:
   - Product image thumbnail
   - Product title
   - Brand name
   - Product ID
   - Clickable link back to ASOS

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | FastAPI + Uvicorn |
| HTTP Client | Requests library |
| Data Processing | Pandas |
| Pattern Matching | Regular Expressions (re) |

---

## Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Could not connect to Backend" | FastAPI server not running | Run `python api.py` first |
| "Please enter a valid ASOS product URL" | Invalid URL/Product ID format | Enter valid ASOS URL or 8-10 digit product ID |
| "Backend API is not responding correctly" | Product ID not found on ASOS | Verify the product ID is valid and in stock |

---

## Notes

- The ASOS API endpoint used is their official internal API (not a scraper)
- Product images are formatted as 320px thumbnails for faster loading
- The application filters primary product images only
- All communication is local (127.0.0.1) unless deployed to a server
