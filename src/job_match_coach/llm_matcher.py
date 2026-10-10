from job_match_coach.models import Resume, JobDescription, MatchResult
from job_match_coach.llm import ask
import json

def match_with_llm(resume: Resume, jd: JobDescription) -> MatchResult:
    prompt = f"""
        你是一个专业的求职助手，你需要：
            比对岗位要求信息{jd.text}和求职者简历{resume.text}，
            并分析出匹配分数（score）和改进建议（suggestions）
        
        要求：必须返回JSON格式（包含score和suggestions）
    """

    raw = json.loads(ask(prompt))

    return MatchResult(score=float(raw["score"]), suggestions=list(raw["suggestions"]))

if __name__ == "__main__":
    print(match_with_llm(Resume(text='熟悉Vue'), JobDescription(text='要求Vue、Python')))