from fastapi import APIRouter
from pydantic import BaseModel
from app.models.cad_generator import generate_model

router = APIRouter()

class DesignRequest(BaseModel):
    prompt: str

@router.post("/generate")
async def generate_file(request: DesignRequest):
    result = generate_model(request.prompt)
    return result