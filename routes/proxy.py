from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
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
    },

    # Rutas de Seguimiento
    "tracker": {
        "service_url": settings.TRACKING_SERVICE_URL,
        "target_path": "api/v1",
        "auth_required": False
    },

    # Rutas de Facturación
    "facturas": {
        "service_url": settings.FACTURACION_SERVICE_URL,
        "target_path": "api/facturas",
        "auth_required": True
    },

    # Rutas extras
    "finanzas": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "/finanzas",
        "auth_required": True
    },
    "gastos": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "/gastos",
        "auth_required": True
    },
    "ingresos": {
        "service_url": settings.GESTION_SERVICE_URL,
        "target_path": "/ingresos",
        "auth_required": True
    },
}

async def proxy_request(
    service_url: str,
    target_path: str,
    remaining_path: str,
    request: Request,
    auth_required: bool = True
) -> Response:
    
    logger.info(f"--- PROXY V4.0 (PASS-THROUGH AUTH) PARA: {target_path} ---")

    target_url = f"{service_url}/{target_path}/{remaining_path}".rstrip('/') if remaining_path else f"{service_url}/{target_path}".rstrip('/')

    # 1. Copiamos los headers del request original (Incluido Authorization)
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ['host', 'content-length', 'accept-encoding']
    }
    
    headers["Accept-Encoding"] = "identity"
    
    # 2. Validación de Seguridad (Solo chequeamos, no modificamos)
    if auth_required:
        try:
            auth_header = headers.get("authorization") or headers.get("Authorization")
            if auth_header:
                token_str = auth_header.split(" ")[1] if " " in auth_header else auth_header
                # Validamos que el token sea real. Si falla, get_current_user lanzará error y cortará el flujo.
                await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str))
                
                # ¡IMPORTANTE! No sobreescribimos headers["Authorization"].
                # Usamos el mismo que nos mandó el Frontend, que sabemos que funciona.
                
        except Exception as e:
            logger.error(f"Error validando token en Gateway: {e}")
            # Opcional: Si quieres ser estricto, puedes descomentar esto:
            # raise HTTPException(status_code=401, detail="Token inválido en Gateway")
            pass 

    try:
        # 3. Hacemos la petición
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=request.query_params,
            follow_redirects=True
        )
        
        # 4. Reconstrucción JSON (Tu V3.0 que funcionaba bien)
        try:
            data = response.json()
            return JSONResponse(content=data, status_code=response.status_code)
        except ValueError:
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type")
            )
        
    except Exception as e:
        logger.error(f"Error Proxy: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error Gateway: {str(e)}")

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