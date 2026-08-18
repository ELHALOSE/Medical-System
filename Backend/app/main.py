from fastapi import FastAPI

from app.routers.auth import router as auth_router


app = FastAPI(
    title="Medical RAG API",
)


app.include_router(auth_router)
