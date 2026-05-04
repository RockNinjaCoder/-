from typing import List, Dict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
import json
from datetime import datetime


class ConversationMemory:
    """
    会话上下文记忆管理器
    支持多会话管理、上下文窗口管理、历史消息持久化
    """

    def __init__(self, max_token_limit: int = 4000):
        """
        初始化记忆管理器

        Args:
            max_token_limit: 最大 token 数量限制，默认 4000
        """
        self.max_token_limit = max_token_limit
        self.conversations: Dict[str, ChatMessageHistory] = {}
        self._load_from_storage()

    def _load_from_storage(self):
        """从存储加载会话历史"""
        pass

    def _save_to_storage(self, session_id: str):
        """保存会话历史到存储"""
        pass

    def get_memory(self, session_id: str) -> ConversationBufferMemory:
        """
        获取指定会话的记忆实例

        Args:
            session_id: 会话 ID

        Returns:
            ConversationBufferMemory 实例
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = ChatMessageHistory()

        memory = ConversationBufferMemory(
            chat_memory=self.conversations[session_id],
            max_token_limit=self.max_token_limit,
            return_messages=True
        )
        return memory

    def add_message(self, session_id: str, role: str, content: str):
        """
        添加消息到指定会话

        Args:
            session_id: 会话 ID
            role: 消息角色 (user/assistant/system)
            content: 消息内容
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = ChatMessageHistory()

        message = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
        self.conversations[session_id].add_message(message)
        self._save_to_storage(session_id)

    def get_messages(self, session_id: str) -> List[BaseMessage]:
        """
        获取指定会话的所有消息

        Args:
            session_id: 会话 ID

        Returns:
            消息列表
        """
        if session_id not in self.conversations:
            return []
        return list(self.conversations[session_id].messages)

    def get_context_window(self, session_id: str, window_size: int = 10) -> List[Dict]:
        """
        获取最近 N 条消息的上下文窗口

        Args:
            session_id: 会话 ID
            window_size: 窗口大小

        Returns:
            消息字典列表
        """
        messages = self.get_messages(session_id)
        recent_messages = messages[-window_size:] if len(messages) > window_size else messages

        context = []
        for msg in recent_messages:
            if isinstance(msg, HumanMessage):
                context.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                context.append({"role": "assistant", "content": msg.content})

        return context

    def clear_session(self, session_id: str):
        """
        清除指定会话的记忆

        Args:
            session_id: 会话 ID
        """
        if session_id in self.conversations:
            self.conversations[session_id].clear()
            self._save_to_storage(session_id)

    def get_token_count(self, session_id: str) -> int:
        """
        计算指定会话的 token 数量

        Args:
            session_id: 会话 ID

        Returns:
            token 数量（估算）
        """
        messages = self.get_messages(session_id)
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4

    def should_compress(self, session_id: str) -> bool:
        """
        检查是否需要压缩上下文

        Args:
            session_id: 会话 ID

        Returns:
            是否需要压缩
        """
        return self.get_token_count(session_id) > self.max_token_limit * 0.8

    def compress_context(self, session_id: str) -> List[Dict]:
        """
        压缩上下文，保留关键信息

        Args:
            session_id: 会话 ID

        Returns:
            压缩后的消息列表
        """
        messages = self.get_messages(session_id)
        if len(messages) <= 4:
            return self.get_context_window(session_id, window_size=len(messages))

        summary_prompt = "请简洁总结以下对话的核心要点，保留关键信息用于后续上下文理解：\n"
        for msg in messages:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            summary_prompt += f"{role}: {msg.content}\n"

        return [{"role": "system", "content": f"对话摘要: (需要 LLM 生成摘要)"}]

    def load_from_db(self, session_id: str, db_conn):
        """
        从数据库加载会话历史

        Args:
            session_id: 会话 ID
            db_conn: 数据库连接
        """
        import asyncio

        async def _load():
            cursor = await db_conn.execute(
                "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,)
            )
            rows = await cursor.fetchall()

            if session_id not in self.conversations:
                self.conversations[session_id] = ChatMessageHistory()

            for row in rows:
                role = row["role"]
                content = row["content"]
                message = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
                self.conversations[session_id].add_message(message)

        asyncio.run(_load())

    def save_to_db(self, session_id: str, db_conn):
        """
        保存会话历史到数据库

        Args:
            session_id: 会话 ID
            db_conn: 数据库连接
        """
        pass


memory_manager = ConversationMemory()