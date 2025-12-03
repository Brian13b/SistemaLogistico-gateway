import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # URLs de tus microservicios
    GESTION_SERVICE_URL: str = os.getenv("GESTION_SERVICE_URL", "http://localhost:8001")
    FACTURACION_SERVICE_URL: str = os.getenv("FACTURACION_SERVICE_URL", "http://localhost:8003")
    TRACKING_SERVICE_URL: str = os.getenv("TRACKING_SERVICE_URL", "http://localhost:8002")
    
    # Configuración del Gateway
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "localhost")
    GATEWAY_PORT: int = os.getenv("GATEWAY_PORT", 8000)
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Timeouts
    REQUEST_TIMEOUT: int = 30
    HEALTH_CHECK_TIMEOUT: int = 5
    
    # Autenticación
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "") 
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")  
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30")) 
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = os.getenv("RATE_LIMIT_REQUESTS") 
    RATE_LIMIT_WINDOW: int = os.getenv("RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"

settings = Settings()