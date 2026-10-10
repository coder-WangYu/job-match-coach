from fastapi import FastAPI
from pydantic import BaseModel
from job_match_coach.llm_matcher import match_with_llm
from job_match_coach.models import Resume, JobDescription
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="求职匹配助手 API")

@app.get("/health")
def health():
    return {"status": "ok"}

# 利用Pydantic模型定义入参 / 出参
class MatchRequest(BaseModel):
    resume: str
    jd: str

class MatchResponse(BaseModel):
    score: float
    suggestions: list[str]

@app.post("/match", response_model=MatchResponse)
def match(body: MatchRequest) -> MatchResponse:
    response = match_with_llm(Resume(text=body.resume), JobDescription(text=body.jd))

    return {
        "score": response.score,
        "suggestions": response.suggestions
    }

# CORS解决浏览器安全限制：允许跨域请求（比如前端 localhost:5173 去请求后端 localhost:8000 ）
app.add_middleware(
    CORSMiddleware, # 处理跨域的中间件
    allow_origins=["*"], # 任何来源都可以（学习方便，生产环境不能这么写）
    allow_methods=["*"], # 允许任何方法
    allow_headers=["*"] # 允许任何请求头
)