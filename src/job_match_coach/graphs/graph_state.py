from typing import TypedDict

class MatchState(TypedDict):
    resume: str
    jd: str
    skills: list[str]
    score: float
    suggestions: list[str]