import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_minimax_llm(
    model: str = "MiniMax-m2.7",
    temperature: float = 0.7,
    streaming: bool = True,
    max_tokens: int = 2048
) -> ChatOpenAI:
    """
    获取 MiniMax LLM 实例

    Args:
        model: 模型名称，默认 MiniMax-m2.7
        temperature: 生成温度，0.0-1.0
        streaming: 是否启用流式输出
        max_tokens: 最大 token 数

    Returns:
        ChatOpenAI 实例
    """
    api_key = os.getenv("MINIMAX_API_KEY")
    api_base = os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")

    if not api_key:
        raise ValueError("MINIMAX_API_KEY 环境变量未设置")

    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base=api_base,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens
    )


def get_minimax_chat():
    """
    获取配置好的 MiniMax 聊天实例（默认配置）
    """
    return get_minimax_llm(
        model="MiniMax-m2.7",
        temperature=0.7,
        streaming=True,
        max_tokens=2048
    )