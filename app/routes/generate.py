from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.gcs import upload_to_gcs

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and store it in GCS. Returns the public URL.
    """
    try:
        url = await upload_to_gcs(file)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
