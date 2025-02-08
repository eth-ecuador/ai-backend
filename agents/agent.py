from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from agents.utils.nodes import agent, generate, rewrite
from agents.utils.state import State
from agents.utils.tools import retrieve_documents

memory = MemorySaver()

workflow = StateGraph(State)

# Define the nodes we will cycle between
workflow.add_node("rewrite", rewrite)  # Re-writing the question
workflow.add_node("agent", agent)  # agent
retrieve = ToolNode([retrieve_documents])

workflow.add_node("retrieve", retrieve)  # retrieval
workflow.add_node(
    "generate", generate
)  # Generating a response after we know the documents

workflow.add_edge(START, "rewrite")
workflow.add_edge("rewrite", "agent")
workflow.add_edge("agent", "retrieve")

workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

graph = workflow.compile(checkpointer=memory)