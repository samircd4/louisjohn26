from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
import time
import os
import shutil
from rich import print
from dotenv import load_dotenv

from helper import download_image_advanced

load_dotenv()

app = FastAPI(title="Product Extractor API")

# Setup environment based dynamic base URL
IS_PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
if IS_PRODUCTION:
    BASE_URL = "http://76.13.243.197:8080"
else:
    BASE_URL = "http://127.0.0.1:8000"

STATIC_ROUTE = "/images"
UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "images"

# Ensure crucial directories exist on startup
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Mount static folder for direct browser image streaming
app.mount(STATIC_ROUTE, StaticFiles(directory=DOWNLOAD_DIR), name="images")

# Read proxy once — passed explicitly into the image downloader
PROXY = os.getenv("PROXY")

MAX_RETRIES = 3


def get_asos_product_id(url: str):
    if "prd/" not in url:
        return None
    return url.split("prd/")[1].split("?")[0].split("#")[0]


def get_asos_price(product_id: str):
    print(f"[cyan]💰 Fetching price for ASOS product ID: {product_id}[/cyan]")
    f_url = f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds={product_id}&store=COM"
    try:
        response = requests.get(f_url, timeout=10)
        if response.status_code == 200:
            data_list = response.json()
            if not data_list:
                return ""
            raw_data = data_list[0]
            price_info = raw_data.get("productPrice", {}).get("current", {}).get("text", "")
            print(f"[green]   Price fetched: {price_info}[/green]")
            return price_info
        else:
            print(f"[red]   Failed to fetch price for product ID {product_id}: Status {response.status_code}[/red]")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"[red]   Error fetching price for product ID {product_id}: {e}[/red]")
        return ""


# --- ASOS Product Extraction Endpoint ---
@app.get("/extract")
def extract_asos(product_url: str):
    product_id = get_asos_product_id(product_url)
    if not product_id:
        raise HTTPException(status_code=400, detail="Invalid ASOS product URL template")

    f_url = f"https://www.asos.com/api/product/catalogue/v4/summaries?productIds={product_id}&store=COM"

    print(f"\n[bold magenta]══════════════════════════════════════[/bold magenta]")
    print(f"[bold magenta]   ASOS EXTRACT REQUEST — ID: {product_id}[/bold magenta]")
    print(f"[bold magenta]══════════════════════════════════════[/bold magenta]")

    last_error = None
    proxies = {"http": PROXY, "https": PROXY}

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n[bold white]── Attempt {attempt}/{MAX_RETRIES} ──[/bold white]")
        try:
            response = requests.get(f_url, proxies=proxies, timeout=10)

            if response.status_code == 200:
                data_list = response.json()

                if not data_list:
                    raise HTTPException(status_code=404, detail="Product not found")

                raw_data = data_list[0]
                images = [f"https://{img.get('url')}" for img in raw_data.get("images", []) if img.get("isPrimary")]
                image_url = f'{images[0]}?$n_640w$&wid=513&fit=constrain' if images else ""
                image_filename = f"product_{product_id}.jpg"

                # ── Image Download Block ──────────────────────────────────
                public_image_url = ""
                if image_url:
                    print(f"[bold cyan]\n🖼  Attempting image download for product {product_id}...[/bold cyan]")
                    # Pass PROXY so helper can route through it on VPS
                    download_data = download_image_advanced(image_url, DOWNLOAD_DIR, image_filename, proxy=PROXY)

                    if download_data and download_data.get("success"):
                        public_image_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{image_filename}"
                        print(f"[bold green]🟢 Image ready at: {public_image_url}[/bold green]")
                    else:
                        error_detail = download_data.get("error", "Unknown error") if download_data else "No response from downloader"
                        print(f"[bold red]🔴 Image download FAILED — product will have no image.[/bold red]")
                        print(f"[red]   Reason: {error_detail}[/red]")
                else:
                    print(f"[yellow]⚠  No primary image URL found for product {product_id} — skipping download.[/yellow]")
                # ─────────────────────────────────────────────────────────

                data = {
                    "title": raw_data.get("name"),
                    "price": get_asos_price(product_id),
                    "brand": raw_data.get("brandName"),
                    "image_url": public_image_url,
                    "url": raw_data.get("pdpUrl")
                }

                print(f"\n[bold green]✅ EXTRACTION COMPLETE — Attempt {attempt}[/bold green]")
                print(f"[green]   Title : {data['title']}[/green]")
                print(f"[green]   Brand : {data['brand']}[/green]")
                print(f"[green]   Price : {data['price']}[/green]")
                print(f"[green]   Image : {data['image_url'] or 'N/A'}[/green]\n")
                return data

            elif response.status_code >= 500:
                last_error = f"Server error {response.status_code}"
                print(f"[yellow]⚠  Attempt {attempt} — {last_error}, will retry...[/yellow]")

            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="ASOS API rejected the request"
                )

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"[red]❌ Attempt {attempt} — Request error: {last_error}[/red]")

        if attempt < MAX_RETRIES:
            wait = 2 ** (attempt - 1)
            print(f"[yellow]   ⏳ Waiting {wait}s before retry...[/yellow]")
            time.sleep(wait)

    print(f"[bold red]💀 ALL {MAX_RETRIES} ATTEMPTS FAILED — {last_error}[/bold red]\n")
    raise HTTPException(
        status_code=500,
        detail=f"Failed after {MAX_RETRIES} attempts: {last_error}"
    )


# --- Zara Product Extraction Endpoint ---
@app.get("/extract-zara")
def extract_zara(product_url: str) -> dict:
    url = f"{product_url}?ajax=true"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "referer": "https://www.zara.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    raw_data = response.json()

    title = raw_data.get("product", {}).get("name")
    price = raw_data.get("productMetaData", [])[0].get("price", "")
    brand = raw_data.get("productMetaData", [])[0].get("brand")
    image = raw_data.get("product", {}).get("detail", {}).get("colors", [])[0].get("mainImgs", [])[0].get("extraInfo", {}).get("deliveryUrl", "")
    pdp_url = raw_data.get("productMetaData", [])[0].get("url")

    product = {
        "title": title,
        "price": f"£{price}",
        "brand": brand,
        "image_url": image if image else "",
        "url": pdp_url
    }
    return product


# --- CSV File Management Endpoints ---
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only .csv files are allowed")

        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File updated/uploaded successfully",
            "filename": filename,
            "path": file_path
        }
    except Exception as e:
        print(f"[red]Error during upload: {e}[/red]")
        raise HTTPException(status_code=500, detail=str(e))


# --- File Download Endpoint ---
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/csv'
    )


# --- List Uploaded Files Endpoint ---
@app.get("/list-files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)