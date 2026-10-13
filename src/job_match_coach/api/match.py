import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from job_match_coach.core.store import RESUME_STORE
from job_match_coach.graphs import chat_graph
from job_match_coach.graphs.graph import graph

router = APIRouter()


# 匹配简历 & JD
class MatchRequest(BaseModel):
    resume_id: str
    jd: str


class MatchResponse(BaseModel):
    score: float
    suggestions: list[str]


@router.post("/match")
def match(body: MatchRequest):
    resume = RESUME_STORE.get(body.resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    response = graph.invoke(
        {
            "resume": resume,
            "jd": body.jd,
            "score": 0,
            "suggestions": [],
        }
    )

    score = response["score"]
    suggestions = response["suggestions"]

    # 把匹配结果、简历、JD，一并塞进对话历史
    config = {"configurable": {"thread_id": body.resume_id}}

    chat_graph.graph.update_state(
        config,
        {
            "messages": [
                {"role": "system", "content": f"简历：{resume}，JD：{body.jd}"},
                {
                    "role": "assistant",
                    "content": f"匹配分：{score}；改进建议：{suggestions}",
                },
            ]
        },
    )

    return {"score": score, "suggestions": suggestions}
