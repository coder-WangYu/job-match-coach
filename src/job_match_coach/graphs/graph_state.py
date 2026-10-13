from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class MatchState(TypedDict):
    resume: str
    jd: str
    skills: list[str]
    score: float
    suggestions: list[str]


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
