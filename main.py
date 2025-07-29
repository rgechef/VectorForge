import os
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
STATIC_DIR = "static"
UPLOADS_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def root():
    return {"status": "VectorForge is alive"}

app.include_router(generate.router, prefix="/api")

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    # Save uploaded file (simulate conversion)
    file_location = os.path.join(UPLOADS_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    # Simulate that we have converted to DXF/STL and provide URL to the uploaded file
    file_url = f"/static/uploads/{file.filename}"

    return {"file_url": file_url, "filename": file.filename, "status": "ready"}

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
        # ... (rest of your block definitions)
    ])

@app.get("/viewer", response_class=HTMLResponse)
async def viewer(request: Request, file: str):
    return templates.TemplateResponse("viewer.html", {
        "request": request,
        "filename": file
    })
