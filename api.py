from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
import requests
import time
import os
import shutil
import uuid
from rich import print
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

PROXIES = {
    "http": os.getenv("PROXY"),
    "https": os.getenv("PROXY")
}

MAX_RETRIES = 3
UPLOAD_DIR = "uploads"


@app.get("/extract")
def extract_asos(product_id: str):
    url = f"https://www.asos.com/api/product/catalogue/v4/summaries?productIds={product_id}&store=COM"

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, proxies=PROXIES, timeout=10)

            # ✅ Success
            if response.status_code == 200:
                data_list = response.json()

                if not data_list:
                    raise HTTPException(status_code=404, detail="Product not found")

                raw_data = data_list[0]

                data = {
                    "title": raw_data.get("name"),
                    "brand": raw_data.get("brandName"),
                    "images": [
                        f"https://{img.get('url')}"
                        for img in raw_data.get("images", [])
                        if img.get("isPrimary")
                    ],
                    "url": raw_data.get("pdpUrl")
                }

                print(f"[SUCCESS] Attempt {attempt}")
                return data

            # 🔁 Retry only on server errors
            elif response.status_code >= 500:
                last_error = f"Server error {response.status_code}"
                print(f"[RETRY] Attempt {attempt} - {last_error}")

            # ❌ Do NOT retry client errors
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="ASOS API rejected the request"
                )

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"[ERROR] Attempt {attempt} - {last_error}")

        # ⏳ Backoff before retry
        if attempt < MAX_RETRIES:
            time.sleep(2 ** (attempt - 1))  # 1s, 2s, 4s

    # ❌ All retries failed
    raise HTTPException(
        status_code=500,
        detail=f"Failed after {MAX_RETRIES} attempts: {last_error}"
    )


# --- CSV File Management Endpoints ---

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

        # Generate a unique filename using UUID to prevent overwriting
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        # Save the file to the local disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "status": "success",
            "saved_as": unique_name,
            "original_name": file.filename
        }
    except Exception as e:
        # Print the error to your local terminal for debugging
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type='text/csv'
    )

@app.get("/list-files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)