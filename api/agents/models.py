from typing import List, Optional
from pydantic import BaseModel

class ClientAttachment(BaseModel):
    name: str
    contentType: str
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str
    toolName: str
    args: dict
    result: dict
    

class ClientMessage(BaseModel):
    role: str
    content: str
    experimental_attachments: Optional[List[ClientAttachment]] = None
    toolInvocations: Optional[List[ToolInvocation]] = None


class AgentRequest(BaseModel):
    messages: List[ClientMessage]
    user_id: str
    thread_id: str
    index_name: str