from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.routers.rag import router as rag_router


app = FastAPI(
    title="Medical RAG API",
)


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(rag_router)