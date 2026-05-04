"""
创建模拟测试数据
"""
import os
import sqlite3
from datetime import datetime, timedelta
import random

DATABASE_PATH = "c:\\Users\\fg\\Documents\\trae_projects\\数据分析\\backend\\data\\analytics.db"

def create_demo_data():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("Creating demo data...")

    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("Demo tables not found, creating...")
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

    # 清空现有数据
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM users")

    # 添加更多用户
    users = [
        ("张三", "zhangsan@example.com"),
        ("李四", "lisi@example.com"),
        ("王五", "wangwu@example.com"),
        ("赵六", "zhaoliu@example.com"),
        ("孙七", "sunqi@example.com"),
        ("周八", "zhouba@example.com"),
        ("吴九", "wujiu@example.com"),
        ("郑十", "zhengshi@example.com"),
    ]

    for username, email in users:
        cursor.execute("""
            INSERT INTO users (username, email, created_at)
            VALUES (?, ?, ?)
        """, (username, email, datetime.now().isoformat()))

    # 添加订单数据
    products = ["笔记本电脑", "无线鼠标", "机械键盘", "显示器", "耳机", "U盘", "移动硬盘", "鼠标垫"]
    prices = [5999.00, 199.00, 399.00, 1299.00, 299.00, 59.00, 399.00, 39.00]

    for i in range(50):
        user_id = random.randint(1, 8)
        product_idx = random.randint(0, len(products) - 1)
        product_name = products[product_idx]
        price = prices[product_idx]
        quantity = random.randint(1, 5)
        created_at = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()

        cursor.execute("""
            INSERT INTO orders (user_id, product_name, quantity, price, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, product_name, quantity, price, created_at))

    conn.commit()

    # 验证数据
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Users: {user_count}")

    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    print(f"Orders: {order_count}")

    # 显示用户列表
    cursor.execute("SELECT id, username, email FROM users")
    print("\nUsers:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} ({row[2]})")

    conn.close()
    print("\nDemo data created successfully!")

if __name__ == "__main__":
    create_demo_data()