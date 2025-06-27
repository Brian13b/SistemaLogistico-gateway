from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
import httpx
import logging
from typing import Dict, Any
from config import settings
from middleware.auth import get_current_user

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

# Configuración optimizada de rutas
ROUTE_MAPPING = {
    # Rutas de Gestión
    "conductores": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/conductores",
        "auth_required": True
    },
    "vehiculos": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/vehiculos",
        "auth_required": True
    },
    "viajes": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/viajes",
        "auth_required": True
    },
    "documentos_conductores": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/documentos_conductores",
        "auth_required": True
    },
    "documentos_vehiculos": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/documentos_vehiculos",
        "auth_required": True
    },
    "documentos_viajes": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "api/documentos_viajes",
        "auth_required": True
    },

    # Rutas de Autenticación
    "auth": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "auth",
        "auth_required": False
    },

    "users": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "auth",
        "auth_required": True
    }
}

async def proxy_request(
    service_url: str,
    target_path: str,
    remaining_path: str,
    request: Request,
    auth_required: bool = True
) -> StreamingResponse:
    """Función central de redirección optimizada"""
    
    # Construcción de URL
    target_url = f"{service_url}/{target_path}/{remaining_path}".rstrip('/') if remaining_path else f"{service_url}/{target_path}".rstrip('/')

    # Preparación de headers
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ['host', 'content-length']
    }
    
    # Manejo de autenticación
    if auth_required:
        if "authorization" not in headers:
            current_user = await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=headers["authorization"].split(" ")[1]))
            headers["Authorization"] = f"Bearer {current_user['token']}"
    
    logger.info(f"Proxying {request.method} {request.url.path} -> {target_url}")
    
    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params
        )
        
        # Filtrado de headers de respuesta
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'server']
        response_headers = {
            key: value for key, value in response.headers.items()
            if key.lower() not in excluded_headers
        }
        response_headers.update({
            "X-Proxied-By": "API-Gateway",
            "X-Target-Service": service_url
        })
        
        return StreamingResponse(
            content=iter([response.content]),
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.ConnectError:
        logger.error(f"Error de conexión con {service_url}")
        raise HTTPException(status_code=503, detail="Servicio no disponible")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del gateway")

# Rutas principales
@router.api_route("/api/{route_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_api_routes(
    route_name: str,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    path_parts = route_name.split('/', 1)
    base_route = path_parts[0]
    remaining_path = path_parts[1] if len(path_parts) > 1 else ""
    
    if not (route_config := ROUTE_MAPPING.get(base_route)):
        raise HTTPException(status_code=404, detail=f"Ruta /api/{base_route} no encontrada")
    
    return await proxy_request(
        service_url=route_config["service_url"],
        target_path=route_config["target_path"],
        remaining_path=remaining_path,
        request=request,
        auth_required=route_config["auth_required"]
    )

@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_auth_routes(path: str, request: Request):
    if not (auth_config := ROUTE_MAPPING.get("auth")):
        raise HTTPException(status_code=503, detail="Servicio de autenticación no configurado")
    
    return await proxy_request(
        service_url=auth_config["service_url"],
        target_path=auth_config["target_path"],
        remaining_path=path,
        request=request,
        auth_required=False
    )

def setup_proxy_routes(app):
    """Integración con FastAPI"""
    app.include_router(router)
    
    @app.on_event("shutdown")
    async def shutdown():
        await client.aclose()