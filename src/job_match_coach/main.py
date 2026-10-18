import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]  # 指向 .../src
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from job_match_coach.api import auth, head_hunter, hr_screen, upload, match, chat

app = FastAPI(title="同频——人岗智配Agent")

@app.get("/health")
def health():
    return {"status": "ok"}

# CORS解决浏览器安全限制：允许跨域请求（比如前端 localhost:5173 去请求后端 localhost:8000 ）
app.add_middleware(
    CORSMiddleware, # 处理跨域的中间件
    allow_origins=["*"], # 任何来源都可以（学习方便，生产环境不能这么写）
    allow_methods=["*"], # 允许任何方法
    allow_headers=["*"] # 允许任何请求头
)

app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(hr_screen.router, prefix="/api/hr")
app.include_router(head_hunter.router, prefix="/api/head-hunter")