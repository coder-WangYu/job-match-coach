from dataclasses import dataclass

@dataclass
class Resume:
    text: str # 个人介绍

@dataclass
class JobDescription:
    text: str # 职位描述

@dataclass
class MatchResult:
    score: float # 0-100匹配分数
    suggestions: list[str] # 改进建议列表