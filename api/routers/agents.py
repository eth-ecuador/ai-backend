import json
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.agent import graph

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class AgentRequest(BaseModel):
    question: str
    thread_id: str

@router.post("/stream")
async def stream(request: AgentRequest):
    inputs = {"messages": [{"role": "user", "content": request.question}]}
    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_stream() -> AsyncGenerator[str, None]:
        async for chunk, metadata in graph.astream(inputs, config, stream_mode="messages"):
            content = chunk.content.strip() if chunk.content else ""
            response_data = {
                "content": content,
                "metadata": metadata
            }
            yield f"data: {json.dumps(response_data)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")