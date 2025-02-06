from langchain_anthropic import ChatAnthropic

from agents.utils.state import State


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}