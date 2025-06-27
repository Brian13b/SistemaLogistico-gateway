import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuración del Gateway API para microservicios de gestión, facturación y tracking.
    """
    
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
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "810a2e72bf922d03c156f5e89d92f6b75359aad6fd3f61f5c25d676894a95353") # Clave secreta para JWT
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")  # Algoritmo de firma
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30")) # 30 minutos por defecto
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = os.getenv("RATE_LIMIT_REQUESTS")  # máximo de peticiones
    RATE_LIMIT_WINDOW: int = os.getenv("RATE_LIMIT_WINDOW")  # ventana de tiempo en segundos
    
    class Config:
        env_file = ".env"

settings = Settings()