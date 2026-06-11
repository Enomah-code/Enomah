import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    agents_used: list[str] = []


def get_raphael():
    from raphael.api.main import get_raphael_instance
    return get_raphael_instance()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Envoie un message à Raphaël et reçoit une réponse orchestrée."""
    session_id = request.session_id or str(uuid.uuid4())
    raphael = get_raphael()

    try:
        response = await raphael.chat(request.message, session_id=session_id)
        return ChatResponse(
            session_id=session_id,
            response=response,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Version streaming: retourne la réponse au fil de l'eau (SSE)."""
    session_id = request.session_id or str(uuid.uuid4())
    raphael = get_raphael()

    async def generate():
        yield f"data: {{\"session_id\": \"{session_id}\"}}\n\n"
        async for chunk in raphael.stream_chat(request.message, session_id=session_id):
            import json
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
