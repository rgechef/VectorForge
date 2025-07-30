import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your API routes
from app.routes import generate

# === FastAPI app initialization ===
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
app.include_router(generate.router)

# === Root endpoint (health check) ===
@app.get("/")
def read_root():
    return {"status": "VectorForge API running"}

# === Optional: Add startup or shutdown events if you need them ===
# @app.on_event("startup")
# async def startup_event():
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     pass
