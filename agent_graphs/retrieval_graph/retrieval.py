"""Manage the configuration of various retrievers.

This module provides functionality to create and manage retrievers for different
vector store backends, specifically Pinecone.

The retrievers support filtering results by user_id to ensure data isolation between users.
"""

import os
from contextlib import contextmanager
from typing import Generator

from langchain_core.embeddings import Embeddings
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings

from agent_graphs.retrieval_graph.configuration import Configuration, IndexConfiguration
from langchain_openai import OpenAIEmbeddings

## Encoder constructors
def make_text_encoder(model: str) -> Embeddings:
    """Connect to the configured text encoder."""
    provider, model = model.split("/", maxsplit=1)
    match provider:
        case "openai":
            return OpenAIEmbeddings(model=model)
        case "sentence-transformers":
            return HuggingFaceEmbeddings(model_name=model)
        case _:
            raise ValueError(f"Unsupported embedding provider: {provider}")


@contextmanager
def make_pinecone_retriever(
    configuration: IndexConfiguration, embedding_model: Embeddings
) -> Generator[VectorStoreRetriever, None, None]:
    """Configure this agent to connect to a specific pinecone index."""
    from langchain_pinecone import PineconeVectorStore

    search_kwargs = configuration.search_kwargs
    index_name = configuration.index_name

    search_filter = search_kwargs.setdefault("filter", {})
    search_filter.update({"user_id": configuration.user_id})
    vstore = PineconeVectorStore.from_existing_index(
        index_name, embedding=embedding_model
    )
    yield vstore.as_retriever()


@contextmanager
def make_retriever(
    config: RunnableConfig,
) -> Generator[VectorStoreRetriever, None, None]:
    """Create a retriever for the agent, based on the current configuration."""
    configuration = IndexConfiguration.from_runnable_config(config)
    embedding_model = make_text_encoder(configuration.embedding_model)
    user_id = configuration.user_id
    
    print("Making retriever")
    if not user_id:
        raise ValueError("Please provide a valid user_id in the configuration.")
    match configuration.retriever_provider:
        case "pinecone":
            with make_pinecone_retriever(configuration, embedding_model) as retriever:
                yield retriever

        case _:
            raise ValueError(
                "Unrecognized retriever_provider in configuration. "
                f"Expected one of: {', '.join(Configuration.__annotations__['retriever_provider'].__args__)}\n"
                f"Got: {configuration.retriever_provider}"
            )