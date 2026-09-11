from typing import Optional
from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    # Supported roles: SUPER_ADMIN, ORG_ADMIN, BRANCH_ADMIN, OPERATOR, VIEWER
    # Legacy aliases: company_admin, inspector, consumer
    role: str = "ORG_ADMIN"
    organization_name: Optional[str] = None
    licence_no: Optional[str] = None
    address: Optional[str] = None
    branch_id: Optional[int] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    organization_id: Optional[int] = None
    branch_id: Optional[int] = None
    is_active: bool


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    organization_id: Optional[int] = None
    branch_id: Optional[int] = None


class LogoutResponse(BaseModel):
    status: str = "success"
    message: str = "Successfully logged out"

