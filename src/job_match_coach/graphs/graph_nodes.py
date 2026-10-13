import json
from unittest import result
from job_match_coach.graphs.graph_state import ChatState, HrScreenState, MatchState
from job_match_coach.llm.llm import ask


def extract_skills(state: MatchState) -> dict:
    prompt = f"""
        从下面的简历中提取技能关键词，只返回JSON数组，例如 ["Python", "Vue"]
        简历：{state["resume"]}
    """

    raw = ask(prompt)
    skills = json.loads(raw)

    return {"skills": skills}


def score_and_suggest(state: MatchState) -> dict:
    prompt = f"""
        你是一个专业的求职助手，你需要：
            比对岗位要求信息{state["jd"]}和求职者简历{state["resume"]}，
            并分析出匹配分数（score）和改进建议（suggestions）
        
        要求：必须返回JSON格式（包含score和suggestions）
    """

    raw = ask(prompt)
    score = json.loads(raw)["score"]
    suggestions = json.loads(raw)["suggestions"]

    return {"score": score, "suggestions": suggestions}


def chat_by_messages(state: ChatState) -> dict:
    prompt = f"""
        你是一个专业的HR/面试官，你需要：
            根据历史对话{state['messages']}回答用户问题
        
        要求：内容精炼，像HR/面试官一样正常对话，不要长篇大论
    """

    raw = ask(prompt)

    return {"messages": [{"role": "assistant", "content": raw}]}


def hr_match_score(state: HrScreenState) -> dict:
    prompt = f"""
        你是一个专业的求职助手，你需要：
            比对岗位要求信息{state["jd"]}和多份求职者简历{state["resumes"]}，
            并分析出每一份简历的匹配分数（score）
        
        要求：只返回 JSON 数组，每项含 resume_id 和 score。
    """

    raw = ask(prompt)
    results = json.loads(raw)

    return {"results": results}
