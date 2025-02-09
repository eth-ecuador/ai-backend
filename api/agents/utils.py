from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage, SystemMessage

from api.agents.schemas import ClientMessage


def parseMessage(message: ClientMessage) -> AnyMessage:
    print("Message:", message)

    if(message.role == "user"):
        return HumanMessage(content=message.content)
    
    if(message.role == "tool"):
        return ToolMessage(content=message.content)
    
    if(message.role == "system"):
        return SystemMessage(content=message.content)