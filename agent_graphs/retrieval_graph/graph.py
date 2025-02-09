"""Main entrypoint for the conversational retrieval graph.

This module defines the core structure and functionality of the conversational
retrieval graph. It includes the main graph definition, state management,
and nodes.
"""

from langgraph.graph import StateGraph, START, END
from agent_graphs.retrieval_graph.nodes import generate_query, answer, retrieve
from agent_graphs.retrieval_graph.configuration import Configuration
from agent_graphs.retrieval_graph.state import InputState, RetrievalGraphState


builder = StateGraph(RetrievalGraphState, input=InputState, config_schema=Configuration)

builder.add_node(generate_query, "generate_query")
builder.add_node(retrieve, "retrieve")
builder.add_node(answer, "answer")

builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)


graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[],
)
graph.name = "RetrievalGraph"