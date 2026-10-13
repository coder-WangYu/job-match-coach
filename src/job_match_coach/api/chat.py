from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from job_match_coach.core.store import RESUME_STORE
from job_match_coach.llm.llm import ask_messages


router = APIRouter()

# 多轮对话
class ChatHistory(BaseModel):
    resume_id: str
    jd: str
    user_text: str

@router.post("/chat")
def chat(body: ChatHistory):
    resume = RESUME_STORE.get(body.resume_id)
    user_message = { "role": "user", "content": body.user_text }

    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    messages = [
        { "role": "system", "content": f"你是一名专业的人岗匹配助手，附上简历摘要{resume} 和 JD {body.jd}，就用户需求给出建议"},
        user_message
    ]

    reply = ask_messages(messages)

    return { "reply": reply }
