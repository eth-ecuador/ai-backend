"""This "graph" simply exposes an endpoint for a user to upload docs to be indexed."""

import logging
from typing import Optional, Sequence

from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.graph import StateGraph, START, END

from agent_graphs.retrieval_graph.retrieval import make_retriever
from agent_graphs.retrieval_graph.configuration import IndexConfiguration
from agent_graphs.index_graph.state import IndexState


def ensure_docs_have_user_id(
    docs: Sequence[Document], config: RunnableConfig
) -> list[Document]:
    """Ensure that all documents have a user_id in their metadata.

        docs (Sequence[Document]): A sequence of Document objects to process.
        config (RunnableConfig): A configuration object containing the user_id.

    Returns:
        list[Document]: A new list of Document objects with updated metadata.
    """
    user_id = config["configurable"]["user_id"]
    print(f"User ID: {user_id}")
    return [
        Document(
            page_content=doc.page_content, metadata={**doc.metadata, "user_id": user_id}
        )
        for doc in docs
    ]

async def index_docs(
    state: IndexState, *, config: Optional[RunnableConfig] = None
) -> dict[str, str]:
    """Asynchronously index documents in the given state using the configured retriever.

    Args:
        state (IndexState): The current state containing documents and retriever.
        config (Optional[RunnableConfig]): Configuration for the indexing process.
    """
    if not config:
        raise ValueError("Configuration required to run index_docs.")
    
    print("Indexing documents...")
    try:
        with make_retriever(config) as retriever:
            stamped_docs = ensure_docs_have_user_id(state.docs, config)
            await retriever.aadd_documents(stamped_docs)
        
        return {"message": "Documents indexed successfully"}
    
    except Exception as e:
        logging.error(f"Error indexing documents: {e}")
        return {"message": str(e)}


builder = StateGraph(IndexState, config_schema=IndexConfiguration)
builder.add_node(index_docs)
builder.add_edge(START, "index_docs")
builder.add_edge("index_docs", END)
graph = builder.compile()

graph.name = "IndexGraph"