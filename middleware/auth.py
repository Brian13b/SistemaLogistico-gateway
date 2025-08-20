from datetime import datetime, timezone
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict, Any
from config import settings
import logging

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Valida el token JWT y retorna el usuario. Si falla, lanza 403."""
    logger = logging.getLogger(__name__)
    if not credentials:
        logger.error("No se proporcionaron credenciales JWT.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credenciales no proporcionadas"
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        if not (username := payload.get("sub")):
            logger.error("Token inválido: usuario no encontrado en el payload.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token inválido: usuario no encontrado"
            )
        
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], timezone.utc):
            logger.error("Token expirado.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token expirado"
            )
        
        return {
            "username": username,
            "token": token,
            "payload": payload
        }
    except JWTError as e:
        logger.error(f"Error de token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Error de token: {str(e)}"
        )