from typing import Literal
from uuid import uuid4
from io import BytesIO
from pypdf import PdfReader
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from job_match_coach.graph import graph
from job_match_coach.db import create_user, get_resume, get_user_by_username, init_db, save_resume
from job_match_coach.supabase_client import get_supabase

app = FastAPI(title="同频——人岗智配Agent")
init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

# 利用Pydantic模型定义入参 / 出参
class MatchRequest(BaseModel):
    resume_id: str
    jd: str

class MatchResponse(BaseModel):
    score: float
    suggestions: list[str]

# 匹配简历 & JD
@app.post("/match", response_model=MatchResponse)
def match(body: MatchRequest) -> MatchResponse:
    # 从SQLite获取简历
    resume = get_resume(body.resume_id)

    if not resume: raise HTTPException(status_code=404, detail="简历不存在")

    response = graph.invoke({
        "resume": resume,
        "jd": body.jd,
        "skills": [],
        "score": 0,
        "suggestions": [],
    })

    return {
        "score": response["score"],
        "suggestions": response["suggestions"]
    }

# 上传简历
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    parts = []

    for page in reader.pages:
        parts.append(page.extract_text() or "")

    text = "\n".join(parts).strip()

    # 创建resume_id
    resume_id = str(uuid4())

    # 存入SQLite
    save_resume(resume_id, text, file.filename)

    return {
        "resume_id": resume_id,
        "filename": file.filename, 
        "size": len(content)
    }

# 用户注册
class UserRegister(BaseModel):
    email: str
    password: str
    role: Literal["job_seeker", "head_hunter", "hr"]

@app.post("/register")
def register(body: UserRegister) -> dict:
    try:
        result = get_supabase().auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {
                    "role": body.role
                }
            }
        })

        return {
            "user_id": result.user.id,
            "email": body.email,
            "role": body.role
        }
    except Exception as e:
        raise HTTPException(400, str(e))

# 用户登录
class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(body: UserLogin) -> dict:
    try:
        result = get_supabase().auth.sign_in_with_password({
            "email": body.email,
            "password": body.password
        })

        return {
            "user_id": result.user.id,
            "email": body.email,
            "role": result.user.user_metadata.get("role")
        }
    
    except Exception as e:
        raise HTTPException(400, str(e))

# CORS解决浏览器安全限制：允许跨域请求（比如前端 localhost:5173 去请求后端 localhost:8000 ）
app.add_middleware(
    CORSMiddleware, # 处理跨域的中间件
    allow_origins=["*"], # 任何来源都可以（学习方便，生产环境不能这么写）
    allow_methods=["*"], # 允许任何方法
    allow_headers=["*"] # 允许任何请求头
)
