import json
from typing import Annotated, AsyncGenerator, List, Optional
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents.agent import graph
from api.routers.models import AgentRequest, ClientMessage
from api.routers.utils import parseMessage

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/stream")
async def stream(request: AgentRequest):
    try:
        inputs = request.messages
        thread_id = request.id

        config = {"configurable": {"thread_id": thread_id}}
        
        state = {
            "messages": [parseMessage(message) for message in inputs],
            "metadata":  {"agent_id": "1"}
        }
        
        print("State:", state)
        
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

        response = StreamingResponse(event_stream(), media_type="text/event-stream")
        response.headers['x-vercel-ai-data-stream'] = 'v1'
        return response
    except Exception as e:
        print("Error:", e)
        return {"error": "Invalid JSON format"}