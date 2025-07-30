from fastapi import APIRouter, File, UploadFile, HTTPException
from utils.gcs import upload_to_gcs
import tempfile

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file to temp file
    suffix = "." + file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Here, convert file as needed (to DXF/STL)
    # For now, just upload original
    with open(tmp_path, "rb") as data:
        url = upload_to_gcs(data, file.filename)
    return {"download_url": url}
