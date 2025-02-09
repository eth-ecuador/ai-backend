from dataclasses import dataclass, field
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Annotated

class DocumentBase(BaseModel):
    type: str
    source: str
    agent_id: UUID

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int

    class Config:
        from_attributes = True


@dataclass(kw_only=True)
class StoreConfig():
    embedding_model: Annotated[
        str,
        {"__template_metadata__": {"kind": "embeddings"}},
    ] = field(
        default="openai/text-embedding-3-small",
        metadata={
            "description": "Name of the embedding model to use. Must be a valid embedding model name."
        },
    )


class StoreRequest(BaseModel):
    messages: List[str]
    id: int = 1


class CreateIndexRequest(BaseModel):
    user_id: str
    index_name: str
    dimension: int = 1536


class AddURLsSourceRequest(BaseModel):
    urls: List[HttpUrl] = Field(..., min_items=1,
                                description="List of URLs to process")
    index_name: str
    user_id: str


class QueryIndexRequest(BaseModel):
    query: str
    index_name: str
