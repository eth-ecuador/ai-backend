from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .agents import router as agents_router
from .stores import router as stores_router

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


app.include_router(agents_router.router)
app.include_router(stores_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}