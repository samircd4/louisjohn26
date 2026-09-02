from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
import os
import shutil
from rich import print
from dotenv import load_dotenv

from brands.cos import get_cos_product
from brands.asos import get_asos_product
from brands.arket import get_arket_product
from brands.zara import get_zara_product

load_dotenv()

app = FastAPI(title="Product Extractor API")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.sarker.shop",
        "localhost",
        "127.0.0.1",
        "app.base44.io",
        ".base44.app",
        "*"  # Allow external VPS IP requests safely
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

STATIC_ROUTE = "/images"
UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app.mount(STATIC_ROUTE, StaticFiles(directory=DOWNLOAD_DIR), name="images")

PROXY = os.getenv("PROXY")
MAX_RETRIES = 3


# --- ASOS Product Extraction Endpoint ---
@app.get("/extract-asos", tags=["Product Extraction"])
def extract_asos(product_url: str, request: Request):
    try:
        return get_asos_product(product_url, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/extract-zara", tags=["Product Extraction"])
def extract_zara(product_url: str, request: Request) -> dict:
    try:
        return get_zara_product(product_url, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/extract-cos", tags=["Product Extraction"])
def extract_cos(product_url: str) -> dict:
    try:
        return get_cos_product(product_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/extract-arket", tags=["Product Extraction"])
def extract_arket(product_url: str):
    try:
        return get_arket_product(product_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/upload-csv", tags=["CSV Management"])
async def upload_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, detail="Only .csv files are allowed")

        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File updated/uploaded successfully",
            "filename": filename,
            "path": file_path
        }
    except Exception as e:
        print(f"[red]Error during upload: {e}[/red]")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}", tags=["CSV Management"])
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/csv'
    )


@app.get("/list-files", tags=["CSV Management"])
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)
