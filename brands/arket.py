# Built in modules
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Installed modules
from selectolax.parser import HTMLParser
from rich import print
from curl_cffi import requests, CurlError
from dotenv import load_dotenv

# Custom modules
from helper import BASE_URL, STATIC_ROUTE, create_thumbnail, _attempt_download, get_bm_s_cookie


load_dotenv()
PROXY = None  # os.getenv('PROXY')
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds


def _load_bm_s_cookie(url: str, force_refresh: bool = False) -> str:
    """Load existing bm_s cookie from file or generate a fresh one if forced/missing."""
    if not force_refresh and os.path.exists("bm_s_cookie.txt"):
        with open("bm_s_cookie.txt", "r") as f:
            cookie_val = f.read().strip()
            if cookie_val:
                print("[cyan]Using existing bm_s cookie from file.[/cyan]")
                return cookie_val

    print("[yellow]Generating fresh Akamai bm_s cookie...[/yellow]")
    fresh_cookie = get_bm_s_cookie(url)
    
    # Fallback to reading file if get_bm_s_cookie wrote to disk but returned None
    if not fresh_cookie and os.path.exists("bm_s_cookie.txt"):
        with open("bm_s_cookie.txt", "r") as f:
            fresh_cookie = f.read().strip()
            
    if fresh_cookie:
        print(f"[green]Acquired fresh bm_s cookie: {fresh_cookie[:25]}...[/green]")
    else:
        print("[red]Warning: Failed to acquire a fresh bm_s cookie.[/red]")
        
    return fresh_cookie or ""


def get_arket_product(url: str) -> dict:
    """Fetch and normalize an Arket product record from its product URL.

    This function requests the product page, handles Akamai anti-bot cookie renewal
    on HTTP 403 or soft challenges, extracts product JSON-LD data, downloads the main
    image, creates a thumbnail, and returns a normalized dictionary.

    Args:
        url (str): The public Arket product URL to scrape.

    Returns:
        dict: A normalized product payload with image and thumbnail URLs, or an
        error dictionary if the request or parsing fails.
    """
    if not url or not url.startswith("http"):
        print("[red]Error: Invalid product URL.[/red]")
        return {
            "error": "Invalid product URL",
            "source": "Arket",
            "url": url,
        }

    try:
        time.sleep(1)  # Sleep briefly to avoid overwhelming server

        # Load initial cookie
        bm_s_cookie = _load_bm_s_cookie(url, force_refresh=False)
        cookies = {"bm_s": bm_s_cookie}

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,bn;q=0.8",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": "https://www.arket.com",
            "sec-ch-ua": '"Not=A?Brand";v="99", "Google Chrome";v="124", "Chromium";v="124"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }

        source = None
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n[bold white]── Arket Fetch Attempt {attempt}/{MAX_RETRIES} ──[/bold white]")
            try:
                response = requests.get(
                    url,
                    cookies=cookies,
                    headers=headers,
                    timeout=20,
                    impersonate="chrome124",
                )

                # Case 1: HTTP 403 Forbidden -> Akamai bot block
                if response.status_code == 403:
                    print(f"[yellow]Attempt {attempt}: Received HTTP 403 Forbidden. Refreshing bm_s cookie...[/yellow]")
                    cookies["bm_s"] = _load_bm_s_cookie(url, force_refresh=True)
                    raise ValueError("HTTP 403 Forbidden — cookie refreshed for retry.")

                # Case 2: Non-200 HTTP status code
                if response.status_code != 200:
                    raise ValueError(f"Failed to fetch product page. Status code: {response.status_code}")

                # Case 3: HTTP 200 but no JSON-LD data -> Akamai soft JS challenge
                html = HTMLParser(response.text)
                scripts = html.css('script[type="application/ld+json"]')
                if not scripts:
                    print(f"[yellow]Attempt {attempt}: No JSON-LD data found (soft challenge). Refreshing bm_s cookie...[/yellow]")
                    cookies["bm_s"] = _load_bm_s_cookie(url, force_refresh=True)
                    raise ValueError("No JSON-LD product data found (anti-bot soft challenge).")

                # Parse JSON-LD product graph
                payload = json.loads(scripts[0].text())
                product_graph = payload.get("@graph", [])
                if not product_graph:
                    raise ValueError("JSON-LD product graph is empty.")

                source = next(
                    (item for item in product_graph if item.get("@type") == "Product"),
                    None,
                )
                if source is None:
                    raise ValueError("No Product entry found in JSON-LD data.")

                print(f"[bold green]✓ Successfully fetched and parsed Arket product on attempt {attempt}![/bold green]")
                break

            except (CurlError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                print(f"[yellow]Attempt {attempt}/{MAX_RETRIES} failed: {exc}[/yellow]")
                if attempt < MAX_RETRIES:
                    print(f"[cyan]Waiting {RETRY_DELAY}s before next attempt...[/cyan]")
                    time.sleep(RETRY_DELAY)

        if source is None:
            raise RuntimeError(f"Failed to fetch Arket product after {MAX_RETRIES} attempts. Last error: {last_error}")

        # Download product image
        images = source.get("image") or []
        if not images:
            raise ValueError("No image URLs found for product.")

        image_url = str(images[0]).split("?")[0]
        image = _attempt_download(image_url, use_http2=True, proxy=PROXY)
        if not isinstance(image, (bytes, bytearray)):
            raise TypeError("Downloaded image payload is invalid.")

        os.makedirs("images", exist_ok=True)
        sku = source.get("sku") or "arket_product"
        image_filename = f"arket_product_{sku}.jpg"
        image_path = os.path.join("images", image_filename)
        with open(image_path, "wb") as f:
            f.write(image)

        thumb_filename = create_thumbnail(image_path)
        public_image_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{image_filename}"
        thumbnail_url = (
            f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{thumb_filename}"
            if thumb_filename
            else ""
        )

        product_data = {
            "id": sku,
            "content_type": "product",
            "source": "Arket",
            "title": source.get("name", "Unknown product"),
            "price": source.get("offers", [{}])[0].get("price", "N/A"),
            "brand": source.get("brand", {}).get("name", "Unknown brand"),
            "image_url": public_image_url,
            "thumbnail_url": thumbnail_url,
            "url": url,
        }

        print(product_data)
        return product_data

    except CurlError as exc:
        print(f"[red]Request error while fetching Arket product: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}
    except (
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
        OSError,
        RuntimeError,
    ) as exc:
        print(f"[red]Failed to parse or save Arket product: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}
    except Exception as exc:
        print(f"[red]Unexpected Arket error: {exc}[/red]")
        return {"error": str(exc), "source": "Arket", "url": url}


if __name__ == "__main__":
    get_arket_product(
        "https://www.arket.com/en-gb/product/relaxed-cotton-jacket-dark-mole-1348122003/"
    )
