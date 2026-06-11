import os
import httpx
from rich import print

# Check environment, default to localhost for testing
IS_PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

if IS_PRODUCTION:
    # Replace with your actual VPS IP or Domain (e.g., "http://your-vps-ip" or "https://sarker.shop")
    BASE_URL = os.getenv("BASE_URL", "http://76.13.243.197:8080/")
else:
    BASE_URL = "http://127.0.0.1:8000"

STATIC_ROUTE = "/images"

def download_image_advanced(url: str, folder_name: str, filename: str) -> dict:
    """
    Downloads an image from a given URL using HTTP/2 protocol and detailed browser headers.
    Returns a dictionary containing execution status, local file path, and public browser URL.
    """
    result = {
        "success": False,
        "local_path": "",
        "public_url": "",
        "error": ""
    }

    print(f"[bold cyan]⬇  IMAGE DOWNLOAD STARTED[/bold cyan]")
    print(f"[cyan]   URL      :[/cyan] {url}")
    print(f"[cyan]   Folder   :[/cyan] {folder_name}")
    print(f"[cyan]   Filename :[/cyan] {filename}")

    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"[yellow]   📁 Created directory: {folder_name}[/yellow]")

        full_path = os.path.join(folder_name, filename)

        # Comprehensive headers mimicking a modern browser profile
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.asos.com/',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }

        print(f"[cyan]   🌐 Sending HTTP/2 request...[/cyan]")

        # HTTP/2 Client configuration
        with httpx.Client(http2=True, headers=headers, timeout=20.0) as client:
            response = client.get(url)
            response.raise_for_status()

            content_length = len(response.content)
            print(f"[cyan]   📦 Response received — Status: {response.status_code} | Size: {content_length} bytes[/cyan]")

            with open(full_path, 'wb') as file:
                file.write(response.content)

        # Confirm file actually exists on disk after write
        if os.path.exists(full_path):
            file_size_kb = os.path.getsize(full_path) / 1024
            print(f"[bold green]✅ IMAGE DOWNLOADED SUCCESSFULLY[/bold green]")
            print(f"[green]   Local Path  : {full_path}[/green]")
            print(f"[green]   File Size   : {file_size_kb:.2f} KB[/green]")
        else:
            print(f"[bold red]❌ FILE WRITE FAILED — file not found on disk after write[/bold red]")
            result["error"] = "File was not written to disk."
            return result

        # Generate browser accessible URL
        public_url = f"{BASE_URL.rstrip('/')}{STATIC_ROUTE}/{filename}"
        print(f"[green]   Public URL  : {public_url}[/green]")

        result["success"] = True
        result["local_path"] = full_path
        result["public_url"] = public_url
        return result

    except httpx.TimeoutException:
        error_msg = "Request timed out — CDN dropped the connection."
        result["error"] = f"Error: {error_msg}"
        print(f"[bold red]❌ IMAGE DOWNLOAD FAILED — TIMEOUT[/bold red]")
        print(f"[red]   Reason : {error_msg}[/red]")

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code} — server rejected the request."
        result["error"] = f"HTTP Error occurred: {e.response.status_code}"
        print(f"[bold red]❌ IMAGE DOWNLOAD FAILED — HTTP ERROR[/bold red]")
        print(f"[red]   Reason : {error_msg}[/red]")

    except Exception as e:
        result["error"] = f"An unexpected error occurred: {e}"
        print(f"[bold red]❌ IMAGE DOWNLOAD FAILED — UNEXPECTED ERROR[/bold red]")
        print(f"[red]   Reason : {e}[/red]")

    return result


if __name__ == "__main__":
    # Test block for running directly via: uv run helper.py
    test_url = "https://images.asos-media.com/products/under-armour-tech-textured-short-sleeve-t-shirt-in-lime/209938091-1-lime?$n_640w$&wid=513&fit=constrain"
    test_folder = "test_download"
    test_file = "product_1.jpg"

    print("\n[bold magenta]══════════════════════════════════[/bold magenta]")
    print("[bold magenta]   RUNNING STANDALONE DOWNLOAD TEST[/bold magenta]")
    print("[bold magenta]══════════════════════════════════[/bold magenta]\n")

    data = download_image_advanced(test_url, test_folder, test_file)

    print(f"\n[bold white]── Final Result Dict ──[/bold white]")
    print(data)