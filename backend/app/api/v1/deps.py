from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User

security_bearer = HTTPBearer(auto_error=False)

# Role normalization mapping
ROLE_NORMALIZATION = {
    "SUPER_ADMIN": "SUPER_ADMIN",
    "super_admin": "SUPER_ADMIN",
    "ORG_ADMIN": "ORG_ADMIN",
    "org_admin": "ORG_ADMIN",
    "company_admin": "ORG_ADMIN",
    "BRANCH_ADMIN": "BRANCH_ADMIN",
    "branch_admin": "BRANCH_ADMIN",
    "OPERATOR": "OPERATOR",
    "operator": "OPERATOR",
    "VIEWER": "VIEWER",
    "viewer": "VIEWER",
    "inspector": "VIEWER",
    "consumer": "VIEWER",
}


def normalize_role(role: Optional[str]) -> str:
    if not role:
        return "VIEWER"
    return ROLE_NORMALIZATION.get(role, role.upper())


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Validates Bearer token and returns current user if present.
    Allows optional authentication for public scanning endpoints.
    """
    if not credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    return user


def require_roles(allowed_roles: list[str]):
    """
    Dependency factory enforcing that authenticated user has one of the allowed roles.
    Supports normalized roles (e.g. ['SUPER_ADMIN', 'ORG_ADMIN']).
    """
    normalized_allowed = {normalize_role(r) for r in allowed_roles}

    def role_checker(current_user: Optional[User] = Depends(get_current_user)) -> User:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        user_norm_role = normalize_role(current_user.role)
        if user_norm_role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Requires one of: {', '.join(sorted(normalized_allowed))}"
            )
        return current_user

    return role_checker


def require_admin_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Enforces authentication and company/super admin privileges."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    norm_role = normalize_role(current_user.role)
    if norm_role not in ["SUPER_ADMIN", "ORG_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Organization administrator role required."
        )
    return current_user


def get_current_active_org_id(current_user: User) -> int:
    """
    Authoritative server-side organization derivation.
    Never trusts arbitrary client organization claims.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any pharmaceutical organization"
        )
    return current_user.organization_id

