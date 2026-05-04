import os
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import httpx

from app.core.llm.minimax_adapter import get_minimax_llm
from app.core.memory.conversation_memory import memory_manager
from app.core.db.connection import get_db


class ChatService:
    """
    聊天服务层
    整合 LLM 调用、上下文记忆、消息存储
    """

    def __init__(self):
        self.llm = get_minimax_llm(streaming=True, temperature=0.7)
        self.api_base = os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")
        self.api_key = os.getenv("MINIMAX_API_KEY")

    async def chat(
        self,
        session_id: str,
        message: str,
        stream: bool = True
    ) -> Dict[str, Any]:
        """
        处理聊天请求

        Args:
            session_id: 会话 ID
            message: 用户消息
            stream: 是否启用流式

        Returns:
            响应字典
        """
        memory_manager.add_message(session_id, "user", message)

        context = memory_manager.get_context_window(session_id, window_size=10)

        system_prompt = "你是一个智能数据分析助手，擅长回答关于数据查询和分析的问题。"
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": message})

        if stream:
            return {
                "type": "streaming",
                "session_id": session_id,
                "messages": messages
            }
        else:
            response = await self._generate_response(messages)
            memory_manager.add_message(session_id, "assistant", response)
            await self._save_message_to_db(session_id, "assistant", response)
            return {
                "type": "response",
                "session_id": session_id,
                "content": response
            }

    async def _generate_response(self, messages: List[Dict]) -> str:
        """生成 LLM 响应"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json={
                        "model": "MiniMax-M2.7",
                        "messages": messages,
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"生成响应失败: {str(e)}"

    async def stream_chat(self, session_id: str, message: str) -> AsyncGenerator[str, None]:
        """
        流式聊天生成器

        Args:
            session_id: 会话 ID
            message: 用户消息

        Yields:
            SSE 格式的数据
        """
        memory_manager.add_message(session_id, "user", message)

        context = memory_manager.get_context_window(session_id, window_size=10)

        system_prompt = "你是一个智能数据分析助手，擅长回答关于数据查询和分析的问题。"
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({"role": "user", "content": message})

        yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    json={
                        "model": "MiniMax-M2.7",
                        "messages": messages,
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "stream": True
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    full_content = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get("choices") and data["choices"][0].get("delta", {}).get("content"):
                                    content = data["choices"][0]["delta"]["content"]
                                    full_content += content
                                    yield f"data: {json.dumps({'type': 'message', 'content': content})}\n\n"
                            except json.JSONDecodeError:
                                pass

            memory_manager.add_message(session_id, "assistant", full_content)
            await self._save_message_to_db(session_id, "assistant", full_content)

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    async def _save_message_to_db(self, session_id: str, role: str, content: str):
        """保存消息到数据库"""
        import uuid
        conn = await get_db()
        message_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        await conn.execute(
            "INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (message_id, session_id, role, content, now)
        )
        await conn.commit()

    def clear_session(self, session_id: str):
        """清除会话记忆"""
        memory_manager.clear_session(session_id)


chat_service = ChatService()