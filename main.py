from fastapi import FastAPI, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import generate
from gcs import upload_file_to_gcs  # <-- Google Cloud integration

app = FastAPI(
    title="VectorForge",
    description="Image to DXF/STL Converter with Smart CAD Blocks",
    version="1.0.0"
)

# ---- CORS Middleware ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (local, if you need them)
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates (if using)
templates = Jinja2Templates(directory="templates")

# Health check
@app.get("/")
def root():
    return {"status": "VectorForge is alive"}

# Include image/CAD generation routes
app.include_router(generate.router, prefix="/api")

# DXF/STL Conversion File Upload Endpoint -- now uploads to Google Cloud Storage!
@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    file_data = await file.read()
    filename = file.filename
    public_url = upload_file_to_gcs(file_data, filename)
    return {
        "filename": filename,
        "url": public_url,
        "status": "uploaded"
    }

# Optional: serve prebuilt smart blocks library
@app.get("/api/blocks")
def get_block_library():
    return JSONResponse(content=[
        {
            "id": "rect_base",
            "name": "RectBase",
            "description": "2D rectangle base with size params",
            "preview_image": "/static/preview/rect_base.png",
            "dxf_file": "/static/dxf/rect_base.dxf"
        },
        # ... other blocks as needed ...
    ])

# STL/OBJ 3D Model Viewer
@app.get("/viewer", response_class=HTMLResponse)
async def viewer(request: Request, file: str):
    return templates.TemplateResponse("viewer.html", {
        "request": request,
        "filename": file
    })
