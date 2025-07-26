from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"],
)

class AIChatRequest(BaseModel):
    message: str
    user_id: int

class AIChatResponse(BaseModel):
    response: str

@router.post("/assistant", response_model=AIChatResponse)
def ai_assistant(request: AIChatRequest):
    # TODO: Fetch CRM context (deals, contacts, etc.) for user_id
    crm_context = "(Mocked CRM context for user_id={})".format(request.user_id)

    # Prepare prompt for Ollama
    prompt = f"CRM Context: {crm_context}\nUser: {request.message}"

    # Call local Ollama API
    try:
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3",  # Using gemma3 model
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        ollama_response.raise_for_status()
        data = ollama_response.json()
        ai_text = data.get("response", "[No response from AI]")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {e}")

    return AIChatResponse(response=ai_text) 