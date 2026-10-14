from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from job_match_coach.core.store import RESUME_STORE
from job_match_coach.graphs import chat_graph
from job_match_coach.graphs.screen_graph import graph


router = APIRouter()


# 简历筛选
class ScreenRequest(BaseModel):
    jd: str
    resume_ids: list[str]


@router.post("/screen")
def screen(body: ScreenRequest):
    resumes = []

    for rid in body.resume_ids:
        resume = RESUME_STORE.get(rid)

        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")

        resumes.append({"resume_id": rid, "resume": resume})

    response = graph.invoke({
        "jd": body.jd,
        "resumes": resumes,
        "results": []
    })

    screenResults = response["results"]

    for result in screenResults:
        category = ""

        if result["score"] >= 85:
            category = "重点关注"
        elif result["score"] >= 60:
            category = "可约面"
        else:
            category = "淘汰"

        result["category"] = category

        # 把匹配分、处理建议、简历、JD，一并塞进对话历史
        resume_id = result["resume_id"]
        config = {"configurable": {"thread_id": resume_id}}
        chat_graph.graph.update_state(
            config,
            {
                "messages": [
                    {"role": "system", "content": f"简历：{RESUME_STORE.get(resume_id)}，JD：{body.jd}"},
                    {
                        "role": "assistant",
                        "content": f"匹配分：{result['score']}；处理建议：{result['category']}",
                    },
                ]
            },
        )

    return {"results": screenResults}
