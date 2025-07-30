from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# === GCS IMPORTS ===
from google.cloud import storage

# === CONFIG ===
BUCKET_NAME = "vectorforge-uploads"  # <--- YOUR BUCKET NAME

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === UPLOAD ENDPOINT ===
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not (file.filename.endswith(".dxf") or file.filename.endswith(".stl")):
        raise HTTPException(status_code=400, detail="Only DXF and STL files allowed.")

    # Save to a temp file
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Upload to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file.filename)
    blob.upload_from_filename(temp_path)

    os.remove(temp_path)
    return {"message": f"{file.filename} uploaded successfully."}

# === DOWNLOAD ENDPOINT ===
@app.get("/download/{filename}")
async def download_file(filename: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    temp_path = f"/tmp/{filename}"
    blob.download_to_filename(temp_path)
    if not os.path.exists(temp_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(temp_path, filename=filename)
