from uuid import uuid4
from io import BytesIO
from pypdf import PdfReader
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from job_match_coach.graph import graph
from job_match_coach.db import create_user, get_resume, get_user_by_username, init_db, save_resume

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

class UserRequest(BaseModel):
    username: str

# 用户注册
@app.post("/register")
def register(body: UserRequest) -> str:
    return create_user(body.username)

# 用户登录
@app.post("/login")
def login(body: UserRequest):
    user = get_user_by_username(body.username)
    if not user: raise HTTPException(404, "用户未注册")

    return {
        "user_id": user,
        "username": body.username
    }

# CORS解决浏览器安全限制：允许跨域请求（比如前端 localhost:5173 去请求后端 localhost:8000 ）
app.add_middleware(
    CORSMiddleware, # 处理跨域的中间件
    allow_origins=["*"], # 任何来源都可以（学习方便，生产环境不能这么写）
    allow_methods=["*"], # 允许任何方法
    allow_headers=["*"] # 允许任何请求头
)
