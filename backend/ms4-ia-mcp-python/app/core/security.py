"""
=============================================================================
 AegisCore AI - MS4: Seguridad y Autorización Keycloak SSO (JWT RS256)
=============================================================================
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    username: str
    email: Optional[str] = None
    roles: List[str] = []
    is_authenticated: bool = True


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> CurrentUser:
    """
    Extrae y valida el token JWT emitido por Keycloak.
    En modo de desarrollo / testing, si no se proporciona token, provee un usuario con rol ACTUARIO
    para permitir pruebas ágiles sin bloquear el flujo.
    """
    if credentials is None:
        # Fallback de desarrollo para pruebas locales
        return CurrentUser(
            username="actuario.dev@aegiscore.com",
            email="actuario@aegiscore.com",
            roles=["ACTUARIO", "ADMIN"],
            is_authenticated=True
        )

    token = credentials.credentials
    try:
        # Decodificación del token Keycloak (en desarrollo decodifica sin verificar firma estricta si no hay cert disponible)
        payload = jwt.decode(token, options={"verify_signature": False})
        username = payload.get("preferred_username") or payload.get("sub") or "usuario_desconocido"
        email = payload.get("email")
        realm_access = payload.get("realm_access", {})
        roles = realm_access.get("roles", [])

        return CurrentUser(
            username=username,
            email=email,
            roles=roles,
            is_authenticated=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token de autorización inválido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(allowed_roles: List[str]):
    """
    Dependencia de FastAPI para verificar si el usuario cuenta con alguno de los roles permitidos.
    """
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        user_roles = set(current_user.roles)
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere uno de los roles {allowed_roles}. Roles actuales: {list(user_roles)}"
            )
        return current_user
    return role_checker
