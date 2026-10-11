from langgraph.graph import StateGraph, START, END
from job_match_coach.graph_state import MatchState
from job_match_coach.graph_nodes import extract_skills, score_and_suggest

builder = StateGraph(MatchState)
builder.add_node("extract_skills", extract_skills)
builder.add_node("score_and_suggest", score_and_suggest)
builder.add_edge(START, "extract_skills")
builder.add_edge("extract_skills", "score_and_suggest")
builder.add_edge("score_and_suggest", END)

graph = builder.compile()
