from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from config import settings
from middleware.cors import setup_cors
from routes.proxy import setup_proxy_routes

app = FastAPI(
    title="API Gateway - Gestión Flotas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

setup_cors(app)

# Configurar rutas
setup_proxy_routes(app)

@app.get("/health")
async def health_check():
    services = {
        "gestión": settings.GESTION_SERVICE_URL,
        "facturación": settings.FACTURACION_SERVICE_URL,
        "tracking": settings.TRACKING_SERVICE_URL
    }
    
    status = {"gateway": "healthy"}
    
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health", timeout=2)
                status[name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                status[name] = "unreachable"
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.GATEWAY_HOST,
        port=settings.GATEWAY_PORT,
        reload=True
    )