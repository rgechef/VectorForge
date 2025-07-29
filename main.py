from fastapi import FastAPI, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import generate

app = FastAPI(
    title="VectorForge",
    description="Image to DXF/STL Converter with Smart CAD Blocks",
    version="1.0.0"
)

# ---- CORS Middleware (allow all for now, restrict later!) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to your actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directory (for STL/OBJ files)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Root health check
@app.get("/")
def root():
    return {"status": "VectorForge is alive"}

# Include image/CAD generation routes
app.include_router(generate.router, prefix="/api")

# --- DXF/STL Conversion File Upload Endpoint (POST /convert) ---
@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    # Echo file info for test -- replace this with your real logic!
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents), "status": "received"}

# Optional: serve prebuilt smart blocks library
@app.get("/api/blocks")
def get_block_library():
    return JSONResponse(content=[
        # ... (your blocks list here, unchanged)
        {
            "id": "rect_base",
            "name": "RectBase",
            "description": "2D rectangle base with size params",
            "preview_image": "/static/preview/rect_base.png",
            "dxf_file": "/static/dxf/rect_base.dxf"
        },
        # ... (rest of your block definitions)
    ])

# STL/OBJ 3D Model Viewer
@app.get("/viewer", response_class=HTMLResponse)
async def viewer(request: Request, file: str):
    return templates.TemplateResponse("viewer.html", {
        "request": request,
        "filename": file
    })
