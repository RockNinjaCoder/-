import os
import aiosqlite
from typing import Optional

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/analytics.db")


class Database:
    _instance: Optional["Database"] = None
    _connection: Optional[aiosqlite.Connection] = None

    def __init__(self):
        self.db_path = DATABASE_PATH

    @classmethod
    async def get_instance(cls) -> "Database":
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    async def get_connection(self) -> aiosqlite.Connection:
        if self._connection is None:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None


async def get_db() -> aiosqlite.Connection:
    db = await Database.get_instance()
    return await db.get_connection()


async def init_database():
    db = await Database.get_instance()
    conn = await db.get_connection()

    await conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '新会话',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS db_schemas (
            id TEXT PRIMARY KEY,
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            column_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS query_logs (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            generated_sql TEXT,
            execution_result TEXT,
            status TEXT CHECK(status IN ('success', 'failed')),
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
        CREATE INDEX IF NOT EXISTS idx_query_logs_session_id ON query_logs(session_id);
    """)

    await conn.commit()
    print("Database initialized successfully")


async def close_database():
    db = await Database.get_instance()
    await db.close()