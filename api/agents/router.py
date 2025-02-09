import json
from typing import Annotated, AsyncGenerator
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from agent_graphs.retrieval_graph.graph import graph
from agent_graphs.retrieval_graph.configuration import Configuration
from agent_graphs.retrieval_graph.state import InputState
from api.agents.models import AgentRequest
from api.agents.utils import parseMessage

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

        response = StreamingResponse(event_stream(), media_type="text/event-stream")
        response.headers['x-vercel-ai-data-stream'] = 'v1'
        return response
    except Exception as e:
        print("Error:", e)
        return {"error": "Invalid JSON format"}