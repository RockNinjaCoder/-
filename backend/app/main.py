from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.core.db.connection import init_database
from app.api import session, chat, query, stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield


app = FastAPI(
    title="智能数据分析系统",
    description="基于 MiniMax-m2.7 + LangChain + FastAPI 的智能数据分析后端服务",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/api/sessions", tags=["会话管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["聊天消息"])
app.include_router(query.router, prefix="/api/query", tags=["数据查询"])
app.include_router(stream.router, prefix="/api/chat", tags=["流式通信"])


@app.get("/")
async def root():
    return {"message": "智能数据分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-api"}