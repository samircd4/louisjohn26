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
from helper import BASE_URL, STATIC_ROUTE, create_thumbnail, _attempt_download, get_html_content


load_dotenv()
PROXY = None  # os.getenv('PROXY')
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds



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
    html_content = get_html_content(url)
    html = HTMLParser(html_content)
    scripts = html.css('script[type="application/ld+json"]')
    if not scripts:
        raise ValueError("No JSON-LD product data found.")

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


if __name__ == "__main__":
    get_arket_product(
        "https://www.arket.com/en-gb/product/relaxed-cotton-jacket-dark-mole-1348122003/"
    )
