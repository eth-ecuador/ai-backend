from typing import Annotated
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from agents.utils.state import State

# URLs to fetch the documents from
urls = [
    "https://docs.arbitrum.io/welcome/arbitrum-gentle-introduction",
    "https://docs.arbitrum.io/welcome/get-started",
    "https://docs.arbitrum.io/for-devs/dev-tools-and-resources/chain-info",
    "https://arbitrum.io/stylus",
    "https://docs.arbitrum.io/stylus/gentle-introduction",
    "https://docs.arbitrum.io/stylus/quickstart",
]

# Function to load documents from URLs
def load_docs(urls):
    docs = []
    for url in urls:
        loader = WebBaseLoader(url)
        docs.extend(loader.load())  # Synchronous document loading
    return docs

# Fetch documents synchronously
docs_list = load_docs(urls)

# Split documents into chunks while preserving metadata
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)
doc_splits = text_splitter.split_documents(docs_list)

# Add metadata to each chunk
for doc in doc_splits:
    doc.metadata["agent_id"] = "1"

# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chroma",
    embedding=OpenAIEmbeddings(),
)
retriever = vectorstore.as_retriever()

@tool
def retrieve_documents(query: str) -> dict:
    """
    Retrieves relevant documents using metadata from the state, appends the results to the messages, 
    and returns both messages and metadata.

    Args:
        query (str): The search query to retrieve relevant documents.
        state (InjectedState): The injected state containing the 'messages' and 'metadata' used for the retrieval process.

    Returns:
        dict: A dictionary containing updated 'messages' and 'metadata'.
    """
    print("---RETRIEVE DOCUMENTS WITH METADATA---")

    print("query", query)
    
    # Retrieve relevant documents based on the query and metadata filter
    search_results = retriever.get_relevant_documents(
        query
    )
    
    print("search_results", search_results)
    

    # Return the updated messages and metadata as a dictionary
    return search_results
