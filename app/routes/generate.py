from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.gcs import upload_to_gcs, download_from_gcs

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        blob_url = await upload_to_gcs(file)  # Will save in 'outputs/' by default
        return {"status": "success", "url": blob_url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    try:
        file_bytes = await download_from_gcs(filename)
        # Guess content type based on extension
        if filename.lower().endswith(".stl"):
            content_type = "application/sla"
        elif filename.lower().endswith(".dxf"):
            content_type = "image/vnd.dxf"
        else:
            content_type = "application/octet-stream"
        return StreamingResponse(
            iter([file_bytes]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}. Error: {e}")
