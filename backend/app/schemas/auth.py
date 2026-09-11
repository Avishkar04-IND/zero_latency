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


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "company_admin"  # company_admin, inspector, consumer
    organization_name: Optional[str] = None
    licence_no: Optional[str] = None
    address: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    organization_id: Optional[int] = None
    is_active: bool
