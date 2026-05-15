from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from typing import Optional
from datetime import datetime

from .enums import TenantStatus, TenantType, OperationType, UserRole, parse_tenant_type, parse_tenant_status


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole
    department: Optional[str] = Field(None, max_length=255)  # For admin/staff
    tenant_id: Optional[int] = None  # For tenant users


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class User(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    department: Optional[str]
    tenant_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    status: str
    message: str
    token: str


class TenantBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    location: str = Field(..., min_length=1, max_length=255)
    floor: int
    area: float = Field(..., gt=0)
    tenant_type: TenantType
    status: TenantStatus = TenantStatus.VACANT

    @field_validator("tenant_type", mode="before")
    @classmethod
    def _coerce_tenant_type(cls, v):
        return parse_tenant_type(v)

    @field_validator("status", mode="before")
    @classmethod
    def _coerce_status(cls, v):
        if v is None:
            return TenantStatus.VACANT
        return parse_tenant_status(v)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    floor: Optional[int] = None
    area: Optional[float] = Field(None, gt=0)
    tenant_type: Optional[TenantType] = None
    status: Optional[TenantStatus] = None

    @field_validator("tenant_type", mode="before")
    @classmethod
    def _coerce_tenant_type(cls, v):
        if v is None:
            return None
        return parse_tenant_type(v)

    @field_validator("status", mode="before")
    @classmethod
    def _coerce_status(cls, v):
        if v is None:
            return None
        return parse_tenant_status(v)


class Tenant(TenantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TenantFilter(BaseModel):
    status: Optional[TenantStatus] = None
    floor: Optional[int] = None
    tenant_type: Optional[TenantType] = None
    area_min: Optional[float] = Field(None, ge=0)
    area_max: Optional[float] = Field(None, ge=0)

    @model_validator(mode="after")
    def _area_max_ge_min(self):
        if (
            self.area_max is not None
            and self.area_min is not None
            and self.area_max < self.area_min
        ):
            raise ValueError("area_max must be greater than or equal to area_min")
        return self


class PaginatedTenants(BaseModel):
    items: list[Tenant]
    total: int
    page: int
    size: int


class AuditLog(BaseModel):
    id: int
    table_name: str
    record_id: int
    operation: str
    old_values: Optional[str]
    new_values: Optional[str]
    user_id: Optional[int]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
