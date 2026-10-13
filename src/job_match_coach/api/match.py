from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from job_match_coach.core.store import RESUME_STORE
from job_match_coach.graphs.graph import graph

router = APIRouter()

# 匹配简历 & JD
class MatchRequest(BaseModel):
    resume_id: str
    jd: str

class MatchResponse(BaseModel):
    score: float
    suggestions: list[str]
    
@router.post("/match", response_model=MatchResponse)
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