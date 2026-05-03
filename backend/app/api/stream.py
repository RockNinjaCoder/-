from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

router = APIRouter()


@router.get("/stream/{session_id}")
async def stream_chat(session_id: str):
    async def event_generator():
        yield "data: {\"type\": \"start\", \"session_id\": \"" + session_id + "\"}\n\n"
        yield "data: {\"type\": \"message\", \"content\": \"流式响应功能开发中...\"}\n\n"
        yield "data: {\"type\": \"end\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )