from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.generate import router as generate_router
from app.routes.routes_ping import router as ping_router

app = FastAPI(
    title="VectorForge",
    description="API for DXF/STL generation and file upload/download",
    version="1.0.0"
)

# === CORS configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Include API routers ===
app.include_router(generate_router)
app.include_router(ping_router)

# === Root endpoint (health check) ===
@app.get("/")
def read_root():
    return {"status": "VectorForge API running"}
