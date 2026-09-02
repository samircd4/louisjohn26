# Built in modules
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Installed modules
from rich import print
from dotenv import load_dotenv
import requests

# Custom modules
from helper import BASE_URL, STATIC_ROUTE, download_image_advanced, extract_product_id

load_dotenv()
PROXY = os.getenv("PROXY")
MAX_RETRIES = 3
DOWNLOAD_DIR = "images"


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


def get_asos_product(product_url: str) -> dict:
    """Fetch and normalize an ASOS product record from its product URL."""
    product_id = extract_product_id(product_url)
    if not product_id:
        raise ValueError("Invalid ASOS product URL template")

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
                    raise ValueError("Product not found")

                raw_data = data_list[0]
                images = [f"https://{img.get('url')}" for img in raw_data.get("images", []) if img.get("isPrimary")]
                image_url = f'{images[0]}?$n_640w$&wid=513&fit=constrain' if images else ""
                image_filename = f"asos_product_{product_id}.jpg"

                public_image_url = ""
                thumbnail_url = ""

                if image_url:
                    print(f"[bold cyan]\n🖼  Attempting image download for product {product_id}...[/bold cyan]")
                    download_data = download_image_advanced(image_url, DOWNLOAD_DIR, image_filename, proxy=PROXY)

                    if download_data and download_data.get("success"):
                        public_image_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{image_filename}"

                        if download_data.get("thumb_filename"):
                            thumbnail_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{download_data['thumb_filename']}"

                        print(f"[bold green]🟢 Image ready at: {public_image_url}[/bold green]")
                        print(f"[bold green]🟢 Thumbnail ready at: {thumbnail_url}[/bold green]")
                    else:
                        error_detail = download_data.get("error", "Unknown error") if download_data else "No response from downloader"
                        print(f"[bold red]🔴 Image download FAILED — product will have no image.[/bold red]")
                        print(f"[red]   Reason: {error_detail}[/red]")
                else:
                    print(f"[yellow]⚠  No primary image URL found for product {product_id} — skipping download.[/yellow]")

                data = {
                    "id": product_id,
                    "content_type": "product",
                    "source": "ASOS",
                    "title": raw_data.get("name"),
                    "price": get_asos_price(product_id),
                    "brand": raw_data.get("brandName"),
                    "image_url": public_image_url,
                    "thumbnail_url": thumbnail_url,
                    "url": raw_data.get("pdpUrl")
                }

                print(f"\n[bold green]✅ EXTRACTION COMPLETE — Attempt {attempt}[/bold green]")
                print(f"[green]   Title     : {data['title']}[/green]")
                print(f"[green]   Brand     : {data['brand']}[/green]")
                print(f"[green]   Price     : {data['price']}[/green]")
                print(f"[green]   Image     : {data['image_url'] or 'N/A'}[/green]")
                print(f"[green]   Thumbnail : {data['thumbnail_url'] or 'N/A'}[/green]\n")
                return data

            elif response.status_code >= 500:
                last_error = f"Server error {response.status_code}"
                print(f"[yellow]⚠  Attempt {attempt} — {last_error}, will retry...[/yellow]")
            else:
                raise ValueError(f"ASOS API rejected the request: {response.status_code}")

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"[red]❌ Attempt {attempt} — Request error: {last_error}[/red]")

        if attempt < MAX_RETRIES:
            wait = 2 ** (attempt - 1)
            print(f"[yellow]   ⏳ Waiting {wait}s before retry...[/yellow]")
            time.sleep(wait)

    print(f"[bold red]💀 ALL {MAX_RETRIES} ATTEMPTS FAILED — {last_error}[/bold red]\n")
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {last_error}")



if __name__ == '__main__':
    test_url = 'https://www.asos.com/asos-design/asos-design-high-neck-slash-shoulder-maxi-dress-with-open-back-in-black/prd/209702624#colourWayId-209702632'
    product_data = get_asos_product(test_url)
    print(product_data)