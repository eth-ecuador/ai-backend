from typing import List, Optional
from pydantic import BaseModel

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    index_name: str

class AgentCreate(AgentBase):
    pass


class Agent(AgentBase):
    id: int

    class Config:
        from_attributes = True
        

# API Models
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