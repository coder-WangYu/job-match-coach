import re

from job_match_coach.models import JobDescription, MatchResult, Resume

# 顿号、逗号、句号、分号；英文逗号和分号一并处理
_JD_SEPARATOR = re.compile(r"[、，。；,;]+")


def match(resume: Resume, jd: JobDescription) -> MatchResult:
    # 如果简历或职位描述为空，则返回0分
    if not resume.text or not jd.text:
        return MatchResult(score=0, suggestions=[])

    # 将职位描述按顿号、逗号、句号、分号分割成多个句子
    segments = [part.strip() for part in _JD_SEPARATOR.split(jd.text) if part.strip()]

    # 计算每个句子与简历的匹配分数
    total_score = 0 # 命中句子数
    suggestions = [] # 改进建议列表
    
    for segment in segments:
        if segment in resume.text:
            total_score += 1
        else:
            suggestions.append(f"职位描述中包含{segment}，但简历中未提及，建议补充")
    
    score = total_score / len(segments) * 100

    return MatchResult(score=score, suggestions=suggestions)

