from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain import hub
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from agents.utils.state import State
from agents.utils.tools import retrieve_documents


llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0, max_tokens=200)

    
def agent(state: State):
    """
    Invokes the agent model to generate a response based on the current state. Given
    the question, use the retriever tool to get relevant documents.

    Args:
        state (messages, metadata): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    print("---CALL AGENT---")
    messages = state["messages"]
    metadata = state["metadata"]

    print ("state", state)
    model = llm.bind_tools([retrieve_documents])
    
    print("Invoking model with")
    response = model.invoke(messages)
    
    # We return a list, because this will get added to the existing list
    return {"messages": [response], "metadata": metadata}

def rewrite(state: State):
    """
    Transform the query to produce a better question.

    Args:
        state (messages, metadata): The current state

    Returns:
        dict: The updated state with re-phrased question
    """

    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    metadata = state["metadata"]
    question = messages[0].content

    msg = [
        HumanMessage(
            content=f""" \n 
    Look at the input and try to reason about the underlying semantic intent / meaning. \n 
    Here is the initial question:
    \n ------- \n
    {question} 
    \n ------- \n
    Formulate an improved question: """,
        )
    ]
    
    print("state", state)

    model = llm
    response = model.invoke(msg)
    return {"messages": [response], "metadata": metadata}


def generate(state):
    """
    Generate answer based on the query and documents retrieved.

    Args:
        state (messages): The current state

    Returns:
         dict: The updated state with answer
    """
    print("---GENERATE---")
    messages = state["messages"]
    metadata = state["metadata"]
    
    question = messages[0].content
    last_message = messages[-1]

    docs = last_message.content

    # Prompt
    prompt = hub.pull("rlm/rag-prompt")

    # LLM
    model = llm

    # Post-processing
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Chain
    rag_chain = prompt | model | StrOutputParser()

    # Run
    response = rag_chain.invoke({"context": docs, "question": question})
    return {"messages": [response], "metadata": metadata}

print("*" * 20 + "Prompt[rlm/rag-prompt]" + "*" * 20)
prompt = hub.pull("rlm/rag-prompt").pretty_print() 