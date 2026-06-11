import os
import httpx
from rich import print

# Check environment, default to localhost for testing
IS_PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    BASE_URL = os.getenv("BASE_URL", "http://76.13.243.197:8080/")
else:
    BASE_URL = "http://127.0.0.1:8000"

STATIC_ROUTE = "/images"

# Comprehensive headers mimicking a modern browser profile
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Referer': 'https://www.asos.com/',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site'
}


def _attempt_download(url: str, use_http2: bool, proxy: str | None) -> bytes:
    """
    Single download attempt with a specific HTTP version and optional proxy.
    Raises on any failure so the caller can try the next strategy.
    """
    proxy_url = proxy or None
    if use_http2:
        client = httpx.Client(
            http2=True,
            headers=BROWSER_HEADERS,
            timeout=20.0,
            proxy=proxy_url
        )
    else:
        # http2=False forces HTTP/1.1 — bypasses RST_STREAM CDN blocks on VPS IPs
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
    """
    Downloads an image from a given URL.
    Strategy:
      1. HTTP/2 with proxy  (if proxy provided)
      2. HTTP/1.1 with proxy (if proxy provided — fallback for CDN RST_STREAM blocks)
      3. HTTP/2 without proxy
      4. HTTP/1.1 without proxy (last resort)

    Returns a dict with success status, local path, public URL, and error info.
    """
    result = {
        "success": False,
        "local_path": "",
        "public_url": "",
        "error": ""
    }

    print(f"\n[bold cyan]⬇  IMAGE DOWNLOAD STARTED[/bold cyan]")
    print(f"[cyan]   URL      : {url}[/cyan]")
    print(f"[cyan]   Folder   : {folder_name}[/cyan]")
    print(f"[cyan]   Filename : {filename}[/cyan]")
    print(f"[cyan]   Proxy    : {proxy if proxy else 'None (direct)'}[/cyan]")

    # Build strategy list: try proxy-first strategies if proxy is available
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

            # Write to disk
            with open(full_path, 'wb') as f:
                f.write(content)

            if os.path.exists(full_path):
                file_size_kb = os.path.getsize(full_path) / 1024
                public_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{filename}"

                print(f"[bold green]✅ IMAGE DOWNLOADED SUCCESSFULLY via {label}[/bold green]")
                print(f"[green]   Local Path  : {full_path}[/green]")
                print(f"[green]   File Size   : {file_size_kb:.2f} KB[/green]")
                print(f"[green]   Public URL  : {public_url}[/green]")

                result["success"] = True
                result["local_path"] = full_path
                result["public_url"] = public_url
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

    # All strategies exhausted
    result["error"] = last_error
    print(f"[bold red]❌ IMAGE DOWNLOAD FAILED — all {len(strategies)} strategies exhausted.[/bold red]")
    print(f"[red]   Last error: {last_error}[/red]")
    return result


if __name__ == "__main__":
    # Test block — uv run helper.py
    import os
    test_url = "https://images.asos-media.com/products/under-armour-tech-textured-short-sleeve-t-shirt-in-lime/209938091-1-lime?$n_640w$&wid=513&fit=constrain"
    test_folder = "test_download"
    test_file = "product_1.jpg"
    test_proxy = os.getenv("PROXY")  # reads from .env if available

    print("\n[bold magenta]══════════════════════════════════[/bold magenta]")
    print("[bold magenta]   RUNNING STANDALONE DOWNLOAD TEST[/bold magenta]")
    print("[bold magenta]══════════════════════════════════[/bold magenta]")

    data = download_image_advanced(test_url, test_folder, test_file, proxy=test_proxy)

    print(f"\n[bold white]── Final Result Dict ──[/bold white]")
    print(data)