import requests
from rich import print

def extract_zara():
    url = "https://www.zara.com/uk/en/striped-short-sleeve-t-shirt-p04424015.html?ajax=true"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,bn;q=0.8",
        "priority": "u=1, i",
        "referer": "https://www.zara.com",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    with open("zara_response.json", "w", encoding="utf-8") as f:
        f.write(response.text)


if __name__ == "__main__":
    extract_zara()