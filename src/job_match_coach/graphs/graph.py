from langgraph.graph import StateGraph, START, END
from job_match_coach.graphs.graph_state import MatchState
from job_match_coach.graphs.graph_nodes import score_and_suggest

builder = StateGraph(MatchState)
builder.add_node("score_and_suggest", score_and_suggest)
builder.add_edge(START, "score_and_suggest")
builder.add_edge("score_and_suggest", END)

graph = builder.compile()
