from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# --- CORS (Enable this if accessing from browser/frontend apps) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to a domain like ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Home Route (Optional) ---
@app.get("/")
def read_root():
    return {"message": "VectorForge API is running."}

# --- Convert Route (GET & POST supported) ---
@app.get("/convert")
@app.post("/convert")
def convert(block_id: str):
    file_path = f"static/dxf/{block_id}.dxf"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='application/dxf', filename=f"{block_id}.dxf")
    else:
        raise HTTPException(status_code=404, detail="File not found")


# --- Optional route to list all blocks (you can delete this if not needed) ---
@app.get("/blocks")
def list_blocks():
    return JSONResponse(content={"message": "List of DXF blocks will go here in future."})
