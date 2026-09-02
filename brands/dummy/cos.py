import json

import requests
from rich import print
from selectolax.parser import HTMLParser

from helper import extract_product_id


def get_cos_product(url: str) -> dict:
    """Fetch and normalize a COS product record from its product URL."""
    if not url or not url.startswith("http"):
        raise ValueError("Invalid COS product URL")

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.cos.com/index.html',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',
    }

    response = requests.get(url, headers=headers, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(f"COS API returned status {response.status_code}")

    html = HTMLParser(response.text)
    script = html.css_first('script[type="application/ld+json"]')
    if script is None:
        raise ValueError("No JSON-LD product data found on the page.")

    data = json.loads(script.text())
    product = {
        'id': extract_product_id(url),
        'content_type': 'product',
        'source': 'COS',
        'title': data.get('name'),
        'price': f"£{data.get('offers', [{}])[0].get('price', '')}",
        'brand': data.get('brand', {}).get('name', ''),
        'image_url': (data.get('image') or [])[0] if data.get('image') else '',
        'url': url,
    }

    print(product)
    return product


def get_cos_with_playwright(url: str):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        html = page.content()
        print(html)
        page.wait_for_timeout(5000)
        browser.close()




if __name__ == '__main__':
    url = 'https://www.cos.com/en-gb/men/menswear/tshirts/regular-fit/product/3-pack-cotton-crew-neck-t-shirts-black-1294699002'
    get_cos_product(url)
