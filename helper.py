import os
import httpx
from PIL import Image
from rich import print
import re
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

# Check environment, default to localhost for testing
IS_PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    BASE_URL = os.getenv("BASE_URL")
    user_data_dir = os.path.abspath("firefox_profile")
else:
    BASE_URL = "http://localhost:8080"
    user_data_dir = r"C:\Users\samir\AppData\Roaming\Mozilla\Firefox\Profiles\xyz123.default-release"

STATIC_ROUTE = "/images"

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site'
}


def extract_product_id(url: str) -> str | None:
    """
    Extracts a product ID from supported store URLs (COS, ASOS, Zara).
    
    Examples:
    - COS  : .../product/3-pack-t-shirts-black-1294699002 -> "1294699002"
    - ASOS : .../prd/209897405#colourWayId=... -> "209897405"
    - Zara : .../running-sneakers-p12382720.html?... -> "12382720"
    """
    if not url:
        return None

    # 1. ASOS: ID comes after '/prd/' and before '?' or '#'
    if "asos.com" in url:
        match = re.search(r'/prd/(\d+)', url)
        if match:
            return match.group(1)

    # 2. Zara: ID comes after '-p' (or '-p0') and before '.html'
    elif "zara.com" in url:
        match = re.search(r'(?:^|[\/\-])(p\d+)(?:\.html)?', url)
        if match:
            return match.group(1)

    # 3. COS: ID is the trailing digits at the end of the URL path
    elif "cos.com" in url:
        clean_path = url.split("?")[0].split("#")[0].rstrip("/")
        match = re.search(r'(\d+)$', clean_path)
        if match:
            return match.group(1)

    # Fallback pattern for generic trailing digits
    fallback_match = re.search(r'(\d+)(?:[?#].*)?$', url)
    if fallback_match:
        return fallback_match.group(1)

    return None



def create_thumbnail(image_path: str, size: tuple = (200, 200)) -> str | None:
    """
    Creates a thumbnail from an existing image file and saves it in the same directory.
    Returns the generated thumbnail's filename.
    """
    try:
        filename, ext = os.path.splitext(image_path)
        thumb_filename = f"{filename}_thumb{ext}"

        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail(size)
            img.save(thumb_filename)

        return os.path.basename(thumb_filename)
    except Exception as e:
        print(f"[red]Failed to create thumbnail: {e}[/red]")
        return None


def _attempt_download(url: str, use_http2: bool, proxy: str | None) -> bytes:
    proxy_url = proxy or None
    if use_http2:
        client = httpx.Client(
            http2=True,
            headers=BROWSER_HEADERS,
            timeout=20.0,
            proxy=proxy_url
        )
    else:
        client = httpx.Client(
            http2=False,
            headers=BROWSER_HEADERS,
            timeout=20.0,
            proxy=proxy_url
        )

    with client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def download_image_advanced(url: str, folder_name: str, filename: str, proxy: str | None = None) -> dict:
    result = {
        "success": False,
        "local_path": "",
        "public_url": "",
        "thumb_filename": "",
        "error": ""
    }

    print(f"\n[bold cyan]⬇  IMAGE DOWNLOAD STARTED[/bold cyan]")
    print(f"[cyan]   URL      : {url}[/cyan]")
    print(f"[cyan]   Folder   : {folder_name}[/cyan]")
    print(f"[cyan]   Filename : {filename}[/cyan]")
    print(f"[cyan]   Proxy    : {proxy if proxy else 'None (direct)'}[/cyan]")

    strategies = []
    if proxy:
        strategies.append({"http2": True,  "proxy": proxy,  "label": "HTTP/2  + Proxy"})
        strategies.append({"http2": False, "proxy": proxy,  "label": "HTTP/1.1 + Proxy"})
    strategies.append(    {"http2": True,  "proxy": None,   "label": "HTTP/2  (direct)"})
    strategies.append(    {"http2": False, "proxy": None,   "label": "HTTP/1.1 (direct)"})

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"[yellow]   📁 Created directory: {folder_name}[/yellow]")

    full_path = os.path.join(folder_name, filename)
    last_error = ""

    for i, strategy in enumerate(strategies, 1):
        label = strategy["label"]
        print(f"[cyan]   🌐 Strategy {i}/{len(strategies)}: {label}...[/cyan]")
        try:
            content = _attempt_download(url, use_http2=strategy["http2"], proxy=strategy["proxy"])

            with open(full_path, 'wb') as f:
                f.write(content)

            if os.path.exists(full_path):
                file_size_kb = os.path.getsize(full_path) / 1024
                public_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{filename}"

                # Generate thumbnail
                thumb_filename = create_thumbnail(full_path)

                print(f"[bold green]✅ IMAGE DOWNLOADED SUCCESSFULLY via {label}[/bold green]")
                print(f"[green]   Local Path     : {full_path}[/green]")
                print(f"[green]   File Size      : {file_size_kb:.2f} KB[/green]")
                print(f"[green]   Public URL     : {public_url}[/green]")
                print(f"[green]   Thumb Filename : {thumb_filename}[/green]")

                result["success"] = True
                result["local_path"] = full_path
                result["public_url"] = public_url
                result["thumb_filename"] = thumb_filename
                return result
            else:
                last_error = "File was not written to disk after successful response."
                print(f"[red]   ⚠  {last_error}[/red]")

        except httpx.RemoteProtocolError as e:
            last_error = f"Protocol error ({label}): {e}"
            print(f"[yellow]   ⚠  Strategy {i} failed — {last_error}[/yellow]")

        except httpx.TimeoutException:
            last_error = f"Timeout ({label}): CDN dropped the connection."
            print(f"[yellow]   ⚠  Strategy {i} failed — {last_error}[/yellow]")

        except httpx.HTTPStatusError as e:
            last_error = f"HTTP {e.response.status_code} ({label})"
            print(f"[yellow]   ⚠  Strategy {i} failed — {last_error}[/yellow]")

        except Exception as e:
            last_error = f"Unexpected error ({label}): {e}"
            print(f"[yellow]   ⚠  Strategy {i} failed — {last_error}[/yellow]")

    result["error"] = last_error
    print(f"[bold red]❌ IMAGE DOWNLOAD FAILED — all {len(strategies)} strategies exhausted.[/bold red]")
    print(f"[red]   Last error: {last_error}[/red]")
    return result


def get_bm_s_cookie(url: str) -> str | None:
    """Fetches a fresh Akamai bm_s cookie using Playwright and returns it."""
    print("\n[cyan]Generating new bm_s cookie...[/cyan]")
    with sync_playwright() as p:
        context = p.firefox.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True
        )
        
        # launch_persistent_context opens a page automatically
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url)
        page.wait_for_load_state('load')  # Wait for the page to load completely
        print(page.title())
        
        cookies = page.context.cookies()
        for cookie in cookies:
            if cookie['name'] == 'bm_s':
                print(f"Found bm_s cookie: {cookie['value']}")
                with open("bm_s_cookie.txt", "w") as f:
                    f.write(cookie['value'])
        context.close()


if __name__ == "__main__":
    get_bm_s_cookie("https://www.cos.com/en-gb/men/menswear/coatsjackets/denim/product/denim-shirt-jacket-blue-1340981001")
