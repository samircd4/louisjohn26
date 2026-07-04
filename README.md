# Product Extraction API

This project provides a FastAPI-based product extraction service for popular fashion retailers. It returns clean product metadata such as title, price, brand, image, and source URL.

Base URL:

- Production: https://api.sarker.shop
- Local: http://127.0.0.1:8000 or http://127.0.0.1:8090

## Supported Endpoints

All endpoints accept a single query parameter named product_url and return a JSON object with product details.

### 1) Extract ASOS Product

Endpoint:

- GET /extract-asos

Example:

```python
import requests

headers = {
    'accept': 'application/json',
}

params = {
    'product_url': 'https://www.asos.com/us/men/t-shirts-and-polos/cat/?cid=4209',
}

response = requests.get('https://api.sarker.shop/extract-asos', params=params, headers=headers)
print(response.json())
```

What you get:

```json
{
  "title": "Product title",
  "price": "Current price text",
  "brand": "Brand name",
  "image_url": "https://.../image.jpg",
  "url": "https://www.asos.com/..."
}
```

### 2) Extract Zara Product

Endpoint:

- GET /extract-zara

Example:

```python
import requests

headers = {
    'accept': 'application/json',
}

params = {
    'product_url': 'https://www.zara.com/us/en/xxx-p123456789.html',
}

response = requests.get('https://api.sarker.shop/extract-zara', params=params, headers=headers)
print(response.json())
```

What you get:

```json
{
  "title": "Product title",
  "price": "£XX",
  "brand": "Brand name",
  "image_url": "https://.../image.jpg",
  "url": "https://www.zara.com/..."
}
```

### 3) Extract COS Product

Endpoint:

- GET /extract-cos

Example:

```python
import requests

headers = {
    'accept': 'application/json',
}

params = {
    'product_url': 'https://www.cos.com/en-gb/men/menswear/tshirts/slim-fit/product/slim-fit-ribbed-henley-t-shirt-navy-mlange-1273213003',
}

response = requests.get('https://api.sarker.shop/extract-cos', params=params, headers=headers)
print(response.json())
```

What you get:

```json
{
  "title": "Product title",
  "price": "£XX",
  "brand": "Brand name",
  "image_url": "https://.../image.jpg",
  "url": "https://www.cos.com/..."
}
```

## Response Fields

Each endpoint returns the same structure:

- title: Product name
- price: Product price as provided by the source site
- brand: Brand name
- image_url: Public image URL if successfully downloaded
- url: Product page URL

## How to Run Locally

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Start the API server

```bash
python api.py
```

The server will run on:

- http://127.0.0.1:8000
- or 8090 if started via the script entrypoint

## Notes

- Make sure to pass the full product URL in the product_url query parameter.
- The API will return an error if the product URL is invalid or the product cannot be found.
- Downloaded images are exposed through the API image route for convenience.
