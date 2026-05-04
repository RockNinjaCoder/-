import os
import json
import asyncio
import httpx
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()


def get_minimax_client():
    api_key = os.getenv("MINIMAX_API_KEY")
    api_base = os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")

    if not api_key:
        raise ValueError("MINIMAX_API_KEY environment variable not set")

    return api_key, api_base


@router.get("/stream/{session_id}")
async def stream_chat(session_id: str, message: str = ""):
    if not message:
        message = "请介绍一下你自己"

    api_key, api_base = get_minimax_client()

    system_prompt = """你是一个智能数据分析助手，擅长将用户的自然语言问题转换为 SQL 查询语句，并返回查询结果。

当用户询问数据相关问题时，你应该：
1. 理解用户想要查询什么数据
2. 生成对应的 SQL 查询语句
3. 执行查询并返回结果

数据库表结构：
- users: id, username, email, created_at
- orders: id, user_id, product_name, quantity, price, created_at

请用中文回答，包含 SQL 语句和查询结果。如果无法回答，请说明原因。"""

    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"

            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{api_base}/chat/completions",
                    json={
                        "model": "MiniMax-M2.7",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "stream": True
                    },
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    yield f"data: {json.dumps({'type': 'end'})}\n\n"
                                else:
                                    try:
                                        data = json.loads(data_str)
                                        if data.get("choices") and data["choices"][0].get("delta", {}).get("content"):
                                            content = data["choices"][0]["delta"]["content"]
                                            yield f"data: {json.dumps({'type': 'message', 'content': content})}\n\n"
                                    except json.JSONDecodeError:
                                        pass

            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        except Exception as e:
            error_msg = str(e)
            print(f"Stream error: {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat")
async def chat(session_id: str, message: str):
    api_key, api_base = get_minimax_client()

    system_prompt = """你是一个智能数据分析助手，擅长将用户的自然语言问题转换为 SQL 查询语句。

数据库表：
- users: id, username, email, created_at
- orders: id, user_id, product_name, quantity, price, created_at

请用中文回答。"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                json={
                    "model": "MiniMax-M2.7",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "stream": False
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )

            result = response.json()

            return {
                "session_id": session_id,
                "model": result.get("model"),
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {})
            }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MiniMax API error: {str(e)}")