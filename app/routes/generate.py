from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.utils.gcs import upload_to_gcs, download_from_gcs

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Upload to GCS (store in 'outputs/' subfolder as per your screenshot)
        blob_url = await upload_to_gcs(file, folder="outputs")
        return {"file_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    try:
        # Downloads from GCS 'outputs/' folder
        file_content = await download_from_gcs(filename, folder="outputs")
        # You can stream file_content as a FileResponse if needed
        return JSONResponse(content={"status": "success", "filename": filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
