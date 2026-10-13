from langgraph.graph import StateGraph, START, END
from job_match_coach.graphs.graph_state import HrScreenState
from job_match_coach.graphs.graph_nodes import hr_match_score

builder = StateGraph(HrScreenState)
builder.add_node("hr_match_score", hr_match_score)
builder.add_edge(START, "hr_match_score")
builder.add_edge("hr_match_score", END)

graph = builder.compile()
