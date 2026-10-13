from langgraph.graph import StateGraph, START, END
from job_match_coach.graphs.graph_state import ChatState
from job_match_coach.graphs.graph_nodes import chat_by_messages
from langgraph.checkpoint.memory import MemorySaver

builder = StateGraph(ChatState)
builder.add_node("chat_by_messages", chat_by_messages)
builder.add_edge(START, "chat_by_messages")
builder.add_edge("chat_by_messages", END)

graph = builder.compile(checkpointer=MemorySaver())
