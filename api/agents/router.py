import json
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from agent_graphs.retrieval_graph.graph import graph
from agent_graphs.retrieval_graph.configuration import Configuration
from agent_graphs.retrieval_graph.state import InputState
from sqlalchemy.orm import Session

from api.agents.utils import parseMessage
from api.database import get_db
from . import crud, schemas

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Agent)
def create_user(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    print("agent", agent)
    return crud.create_agent(db=db, agent=agent)


@router.get("/", response_model=list[schemas.Agent])
def get_agents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    agents = crud.get_agents(db, skip=skip, limit=limit)
    return agents


@router.get("/{agent_id}", response_model=schemas.Agent)
def get_one_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.delete_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent


@router.post("/stream")
async def stream(request: schemas.AgentRequest):
    try:
        inputs = request.messages

        config: Configuration = {"configurable": {
            "index_name": request.index_name,
            "user_id": request.user_id,
            "embedding_model": "openai/text-embedding-3-small",
            "retriever_provider": "pinecone",
            "search_kwargs": {},
            "response_model": "anthropic/claude-3-5-sonnet-20240620",
            "query_model": "anthropic/claude-3-haiku-20240307",
            "thread_id": request.thread_id
        }}

        state: InputState = {
            "messages": [parseMessage(message) for message in inputs]
        }

        async def event_stream() -> AsyncGenerator[str, None]:
            accumulated_metadata = {}
            async for chunk, metadata in graph.astream(state, config, stream_mode="messages"):
                content = chunk.content if chunk.content else ""
                if content:
                    print(f"0:{json.dumps(content)}\n")
                    yield f"0:{json.dumps(content)}\n"
                accumulated_metadata = metadata  # Accumulate metadata from the last chunk

            # Send final 'd:' event with finish reason and usage
            finish_reason = "stop"
            usage = accumulated_metadata.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            yield f'd:{{"finishReason":"{finish_reason}","usage":{{"promptTokens":{prompt_tokens},"completionTokens":{completion_tokens}}}}}\n'

        response = StreamingResponse(
            event_stream(), media_type="text/event-stream")
        response.headers['x-vercel-ai-data-stream'] = 'v1'
        return response
    except Exception as e:
        print("Error:", e)
        return {"error": "Invalid JSON format"}
