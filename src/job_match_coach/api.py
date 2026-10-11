from uuid import uuid4
from io import BytesIO
from pypdf import PdfReader
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from job_match_coach.graph import graph

app = FastAPI(title="求职匹配助手 API")

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

# 维护映射：resume_id -> resume.text
RESUME_STORE: dict[str, str] = {}

# 匹配简历 & JD
@app.post("/match", response_model=MatchResponse)
def match(body: MatchRequest) -> MatchResponse:
    resume = RESUME_STORE.get(body.resume_id)

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
    RESUME_STORE[resume_id] = text

    return {
        "resume_id": resume_id,
        "filename": file.filename, 
        "size": len(content)
    }

# CORS解决浏览器安全限制：允许跨域请求（比如前端 localhost:5173 去请求后端 localhost:8000 ）
app.add_middleware(
    CORSMiddleware, # 处理跨域的中间件
    allow_origins=["*"], # 任何来源都可以（学习方便，生产环境不能这么写）
    allow_methods=["*"], # 允许任何方法
    allow_headers=["*"] # 允许任何请求头
)