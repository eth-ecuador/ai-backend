from langchain_core.messages import HumanMessage, ToolMessage

from typing import AsyncGenerator, cast

async def stream_with_errors(generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    try:
        async for chunk in generator:
            yield chunk
    
    # You can have your own custom exceptions.
    except Exception as e:
        # you may choose to return a generic error or risk it with str(e)
        error_msg = "An error occurred and our developers were notified"
        yield f"event: error_event\ndata: {error_msg}\n\n"
