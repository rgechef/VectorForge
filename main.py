import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse
from google.cloud import storage

# --------- CONFIG ---------
GCP_BUCKET = "vectorforge-uploads"
GCP_CREDENTIALS = "/etc/secrets/gcp-key.json"  # Don't change unless you use a different secret file path
GCS_OUTPUTS_DIR = "outputs/"

# --------- APP & CORS ---------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: replace with your Vercel domain for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gcs_client():
    return storage.Client.from_service_account_json(GCP_CREDENTIALS)

# --------- ROUTES ---------
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".dxf", ".stl")):
        raise HTTPException(status_code=400, detail="Only DXF/STL files allowed.")

    client = get_gcs_client()
    bucket = client.bucket(GCP_BUCKET)
    blob = bucket.blob(f"{GCS_OUTPUTS_DIR}{file.filename}")

    try:
        contents = await file.read()
        blob.upload_from_string(contents)
        url = blob.public_url
        return {"filename": file.filename, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/download/{filename}")
def download_file(filename: str):
    if not filename.lower().endswith((".dxf", ".stl")):
        raise HTTPException(status_code=400, detail="Only DXF/STL files allowed.")

    client = get_gcs_client()
    bucket = client.bucket(GCP_BUCKET)
    blob = bucket.blob(f"{GCS_OUTPUTS_DIR}{filename}")

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    # Download to a temp location in the container
    local_path = f"/tmp/{filename}"
    blob.download_to_filename(local_path)
    return FileResponse(local_path, filename=filename, media_type="application/octet-stream")

@app.get("/")
def root():
    return JSONResponse({"status": "VectorForge backend API running."})
