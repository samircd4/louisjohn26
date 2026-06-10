import os
import httpx

def download_image_advanced(url: str, folder_name: str, filename: str) -> str:
    """
    Downloads an image from a given URL using HTTP/2 protocol and detailed browser headers.
    
    This function is designed to bypass strict anti-bot and CDN protections (like Cloudflare or Akamai)
    by mimicking a real browser fingerprint and connection profile.

    Args:
        url (str): The direct target URL or CDN endpoint of the image to download.
        folder_name (str): The local directory directory path where the image will be saved (creates folder if missing).
        filename (str): The target name of the saved file (e.g., 'product_image.jpg').

    Returns:
        str: The full local path to the saved image file if successful, or an empty string ("") if the download fails.
    """
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            
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
        
        # Using httpx Client with HTTP/2 support to mimic browser network layer
        with httpx.Client(http2=True, headers=headers, timeout=20.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            with open(full_path, 'wb') as file:
                file.write(response.content)
                
        print(f"Success! Image saved to: {full_path}")
        return full_path

    except httpx.TimeoutException:
        print("Error: The request timed out. ASOS CDN is still dropping the connection.")
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error occurred: {e.response.status_code} - {e.response.reason_phrase}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return ""

if __name__ == "__main__":
    image_url = "https://images.asos-media.com/products/under-armour-tech-textured-short-sleeve-t-shirt-in-lime/209938091-1-lime?$n_640w$&wid=513&fit=constrain"
    folder_name = "downloaded_images"
    file_name = "under_armour_tee_fixed.jpg"
    
    download_image_advanced(image_url, folder_name, file_name)