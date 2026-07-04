import requests
import json
from rich import print



def get_cos(url):
    headers = {
        'accept': 'application/json',
    }

    params = {
        'product_url': url,
    }

    response = requests.get('http://127.0.0.1:8080/extract-cos', params=params, headers=headers)

    data = response.json()

    print(data)



for i, j in enumerate(range(1, 400)):
    url = 'https://www.cos.com/en-gb/men/menswear/tshirts/slim-fit/product/slim-ribbed-t-shirt-black-1229297002'
    get_cos(url)
    print(f"Scraped {i+1} products")
    