from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class MatchState(TypedDict):
    resume: str
    jd: str
    score: float
    suggestions: list[str]


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


class HrScreenState(TypedDict):
    jd: str
    resumes: list[dict]
    results: list[dict]
