from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

def setup_cors(app: FastAPI) -> None:
    """Configura CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-API-Version"]
    )