from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import agents

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, adjust as necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


app.include_router(agents.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}