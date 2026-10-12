import sqlite3
from pathlib import Path
from uuid import uuid4

DB_PATH = Path("data/app.db")

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        # 创建简历表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                filename TEXT
            )
            """
        )

        # 创建用户表
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL
            )
            """
        )

def save_resume(id, text, filename):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO resumes (id, text, filename) VALUES (?, ?, ?)",
            (id, text, filename)
        )

def get_resume(id) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT text FROM resumes WHERE id = ?",
            (id,) # 在 Python 里，(id) 只是给 id 加括号，还是单个值；单元素元组必须带逗号：(id,)
        ).fetchone()

    # with 管的是连接何时关闭，不会限制变量作用域。
    # row 在函数里赋值后，出了 with 仍然能用；关掉的是 conn。
    return row[0] if row else None

def create_user(username: str) -> str:
    user_id = str(uuid4())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO users (id, username) VALUES (?, ?)",
            (user_id, username)
        )
    
    return user_id

def get_user_by_username(username: str) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    return row[0] if row else None