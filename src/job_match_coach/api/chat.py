from fastapi import APIRouter
from pydantic import BaseModel
from job_match_coach.graphs.chat_graph import graph

router = APIRouter()


# 多轮对话
class ChatRequest(BaseModel):
    resume_id: str
    jd: str
    user_text: str


@router.post("/chat")
def chat(body: ChatRequest):
    user_message = {"role": "user", "content": body.user_text}

    response = graph.invoke(
        {"messages": [user_message]},
        config={"configurable": {"thread_id": body.resume_id}},
    )

    reply = response["messages"][-1].content

    return {"reply": reply}
