"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Any, Literal, Optional, Type, TypeVar

from langchain_core.runnables import RunnableConfig, ensure_config

from agent_graphs.index_graph.configuration import IndexConfiguration
from agent_graphs.retrieval_graph.prompts import QUERY_SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT


@dataclass(kw_only=True)
class Configuration(IndexConfiguration):
    """The configuration for the agent."""

    response_system_prompt: str = field(
        default=RESPONSE_SYSTEM_PROMPT,
        metadata={"description": "The system prompt used for generating responses."},
    )

    response_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-5-sonnet-20240620",
        metadata={
            "description": "The language model used for generating responses. Should be in the form: provider/model-name."
        },
    )

    query_system_prompt: str = field(
        default=QUERY_SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt used for processing and refining queries."
        },
    )

    query_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-haiku-20240307",
        metadata={
            "description": "The language model used for processing and refining queries. Should be in the form: provider/model-name."
        },
    )