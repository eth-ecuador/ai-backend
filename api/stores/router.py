from fastapi import APIRouter, Query, Depends
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import SeleniumURLLoader
from sqlalchemy.orm import Session

from agent_graphs.index_graph.graph import graph
from agent_graphs.index_graph.configuration import IndexConfiguration
from agent_graphs.index_graph.state import IndexState
from api.database import get_db
from api.stores.crud import create_document, get_documents
from api.stores.schemas import DocumentCreate, AddURLsSourceRequest, CreateIndexRequest, QueryIndexRequest
from api.stores.utils import vector_db

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def createIndex(request: CreateIndexRequest):
    index_name = request.index_name
    dimension = request.dimension

    index = vector_db.describe_index(index_name)

    if index:
        return {"message": "Index already exists"}

    print("Creating index...")
    vector_db.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    return {"message": "Index created successfully, waiting for index to be ready..."}


@router.delete("/")
async def deleteIndex(index_name: str = Query(..., min_length=3, max_length=50)):
    print("Deleting index...")
    result = vector_db.delete_index(index_name)

    return {"message": result}


@router.get("/")
async def listIndexes(
    index_name: str = Query(..., min_length=3, max_length=50),
):
    index = vector_db.describe_index(index_name)
    serialized_index = {}
    for key, value in index.__dict__.items():
        if isinstance(value, (str, int, float, bool, list, dict)):
            serialized_index[key] = value
        else:
            serialized_index[key] = str(value)

    return {"index": serialized_index}


@router.post("/urls")
async def addURLs(request: AddURLsSourceRequest, db: Session = Depends(get_db)):
    config: IndexConfiguration = {"configurable": {
        "index_name": request.index_name,
        "user_id": request.user_id,
        "retriever_provider": "pinecone",
        "search_kwargs": {},
    }}

    print("Loading docs...")
    loader = SeleniumURLLoader(urls=[str(url) for url in request.urls])
    documents = loader.load()

    print("Splitting...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    initial_state: IndexState = {
        "docs": docs
    }

    "Uploading to Pinecone"
    result = await graph.ainvoke(initial_state, config)
    print(result)
    
    print("Creating documents...")
    for url in request.urls:
        create_document(db=db, document=DocumentCreate(type="url", source=str(url), agent_id=request.user_id))

    return {"message": result}


@router.get("/docs")
async def getDocs(agent_id: str = Query(..., min_length=3, max_length=50), db: Session = Depends(get_db)):
    result = get_documents(db=db, agent_id=agent_id, limit=30)

    return result


@router.post("/docs")
async def createDocs(document=DocumentCreate, db: Session = Depends(get_db)):
    result = create_document(db=db, document=document)

    return {"message": result}


@router.get("/query")
async def queryIndex(request: QueryIndexRequest):
    query = request.query
    index_name = request.index_name

    embeddings = OpenAIEmbeddings()

    print("query", query)
    vectorstore = PineconeVectorStore(
        index_name=index_name, embedding=embeddings)

    result = vectorstore.similarity_search(query, k=10)

    return {"message": result}
