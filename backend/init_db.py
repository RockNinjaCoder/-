import os
import sqlite3
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/analytics.db")


def init_database_sync():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '新会话',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_schemas (
            id TEXT PRIMARY KEY,
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            column_type TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
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
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_logs_session_id ON query_logs(session_id)")

    conn.commit()
    conn.close()

    print(f"Database initialized at: {DATABASE_PATH}")


def create_demo_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO db_schemas (id, table_name, column_name, column_type, description)
        VALUES
            ('schema-users-1', 'users', 'id', 'INTEGER', '用户ID，主键'),
            ('schema-users-2', 'users', 'username', 'TEXT', '用户名，唯一'),
            ('schema-users-3', 'users', 'email', 'TEXT', '邮箱'),
            ('schema-users-4', 'users', 'created_at', 'TIMESTAMP', '创建时间'),
            ('schema-orders-1', 'orders', 'id', 'INTEGER', '订单ID，主键'),
            ('schema-orders-2', 'orders', 'user_id', 'INTEGER', '用户ID，外键'),
            ('schema-orders-3', 'orders', 'product_name', 'TEXT', '产品名称'),
            ('schema-orders-4', 'orders', 'quantity', 'INTEGER', '数量'),
            ('schema-orders-5', 'orders', 'price', 'REAL', '价格'),
            ('schema-orders-6', 'orders', 'created_at', 'TIMESTAMP', '创建时间')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email) VALUES
            ('zhangsan', 'zhangsan@example.com'),
            ('lisi', 'lisi@example.com'),
            ('wangwu', 'wangwu@example.com')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO orders (user_id, product_name, quantity, price) VALUES
            (1, 'Product A', 2, 99.99),
            (1, 'Product B', 1, 149.99),
            (2, 'Product A', 3, 99.99),
            (3, 'Product C', 1, 199.99)
    """)

    conn.commit()
    conn.close()

    print("Demo tables created successfully")


if __name__ == "__main__":
    init_database_sync()
    create_demo_tables()
    print("Database initialization complete!")