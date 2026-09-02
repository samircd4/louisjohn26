import os
import json
import time
import requests
from rich import print

from helper import BASE_URL, STATIC_ROUTE, download_image_advanced, extract_product_id

PROXY = os.getenv("PROXY")
MAX_RETRIES = 3


def get_zara_product(product_url: str, request=None) -> dict:
    """Fetch and normalize a Zara product record from its product URL.

    The function validates the product URL, requests Zara's AJAX product payload,
    downloads a local image copy into the images directory, creates a thumbnail,
    and returns the normalized product record for downstream API usage.

    Args:
        product_url (str): The public Zara product URL.
        request (Request | None): Optional FastAPI request object used to build
            the public image URLs from the current host.

    Returns:
        dict: A normalized Zara product payload containing product metadata and
        public image URLs.
    """
    if not product_url or not product_url.startswith("http"):
        raise ValueError("Invalid Zara product URL")

    product_id = extract_product_id(product_url)
    if not product_id:
        raise ValueError("Could not extract product ID from Zara URL")

    ajax_url = product_url if "?ajax=true" in product_url else f"{product_url}?ajax=true"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "referer": "https://www.zara.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }

    print(f"\n[bold magenta]══════════════════════════════════════[/bold magenta]")
    print(f"[bold magenta]   ZARA EXTRACT REQUEST[/bold magenta]")
    print(f"[bold magenta]   URL: {product_url}[/bold magenta]")
    print(f"[bold magenta]══════════════════════════════════════[/bold magenta]")

    last_error = None
    base_url = str(request.base_url).rstrip("/") if request else BASE_URL.rstrip("/")

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n[bold white]── Attempt {attempt}/{MAX_RETRIES} ──[/bold white]")
        try:
            response = requests.get(ajax_url, headers=headers, timeout=15)
            if response.status_code != 200:
                last_error = f"Zara API returned status {response.status_code}"
                print(f"[red]❌ {last_error}[/red]")
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** (attempt - 1))
                    continue
                raise RuntimeError(last_error)

            raw_data = response.json()
            product = raw_data.get("product", {}) or {}
            product_meta = raw_data.get("productMetaData", [])
            meta = product_meta[0] if isinstance(product_meta, list) and product_meta else {}

            title = product.get("name") or meta.get("name") or "Unknown product"
            price = meta.get("price") or ""
            brand = meta.get("brand") or "Zara"
            pdp_url = meta.get("url") or product_url

            image_source_url = ""
            colors = product.get("detail", {}).get("colors", []) if isinstance(product.get("detail", {}), dict) else []
            for color in colors:
                if not isinstance(color, dict):
                    continue
                for image in color.get("mainImgs", []):
                    if not isinstance(image, dict):
                        continue
                    for field in ("deliveryUrl", "url", "imageUrl", "image_url", "src"):
                        value = image.get(field)
                        if value:
                            image_source_url = value
                            break
                    if image_source_url:
                        break
                if image_source_url:
                    break

            if image_source_url.startswith("//"):
                image_source_url = f"https:{image_source_url}"

            public_image_url = ""
            thumbnail_url = ""
            if image_source_url:
                print(f"[bold cyan]\n🖼  Attempting image download for Zara product {product_id}...[/bold cyan]")
                image_filename = f"zara_product_{product_id}.jpg"
                download_data = download_image_advanced(
                    image_source_url,
                    "images",
                    image_filename,
                    proxy=PROXY,
                )

                if download_data and download_data.get("success"):
                    public_image_url = f"{base_url}{STATIC_ROUTE}/{image_filename}"
                    if download_data.get("thumb_filename"):
                        thumbnail_url = f"{base_url}{STATIC_ROUTE}/{download_data['thumb_filename']}"
                    print(f"[bold green]🟢 Image ready at: {public_image_url}[/bold green]")
                    print(f"[bold green]🟢 Thumbnail ready at: {thumbnail_url}[/bold green]")
                else:
                    error_detail = download_data.get("error", "Unknown error") if download_data else "No response from downloader"
                    print(f"[bold red]🔴 Image download FAILED — product will have no image.[/bold red]")
                    print(f"[red]   Reason: {error_detail}[/red]")
            else:
                print(f"[yellow]⚠  No image URL found for product {product_id} — skipping download.[/yellow]")

            product_data = {
                "id": product_id,
                "content_type": "product",
                "source": "Zara",
                "title": title,
                "price": f"£{price}" if str(price).replace(".", "", 1).isdigit() else price,
                "brand": brand,
                "image_url": public_image_url,
                "thumbnail_url": thumbnail_url,
                "url": pdp_url,
            }

            print(f"\n[bold green]✅ EXTRACTION COMPLETE — Attempt {attempt}[/bold green]")
            print(f"[green]   Title     : {product_data['title']}[/green]")
            print(f"[green]   Brand     : {product_data['brand']}[/green]")
            print(f"[green]   Price     : {product_data['price']}[/green]")
            print(f"[green]   Image     : {product_data['image_url'] or 'N/A'}[/green]")
            print(f"[green]   Thumbnail : {product_data['thumbnail_url'] or 'N/A'}[/green]\n")
            return product_data

        except requests.exceptions.RequestException as exc:
            last_error = str(exc)
            print(f"[red]❌ Attempt {attempt} — Request error: {last_error}[/red]")
        except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError, OSError) as exc:
            last_error = str(exc)
            print(f"[red]❌ Attempt {attempt} — Data error: {last_error}[/red]")
        except Exception as exc:
            last_error = str(exc)
            print(f"[red]❌ Attempt {attempt} — Unexpected error: {last_error}[/red]")

        if attempt < MAX_RETRIES:
            wait = 2 ** (attempt - 1)
            print(f"[yellow]   ⏳ Waiting {wait}s before retry...[/yellow]")
            time.sleep(wait)

    print(f"[bold red]💀 ALL {MAX_RETRIES} ATTEMPTS FAILED — {last_error}[/bold red]\n")
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {last_error}")


if __name__ == "__main__":
    test_url = "https://www.zara.com/us/en/zw-collection-embroidered-cape-blouse-p05107249.html"
    print(get_zara_product(test_url))
