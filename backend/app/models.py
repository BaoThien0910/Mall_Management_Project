from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func, Enum as SQLEnum, ForeignKey

from .db import Base
from .enums import TenantStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(
        SQLEnum(
            UserRole,
            name="userrole",
            native_enum=False,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=UserRole.STAFF,
    )
    department = Column(String(255), nullable=True)  # For admin/staff
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # For tenant users linked to a tenant
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # default=func.now() so INSERT succeeds if the DB column has no DEFAULT (e.g. old migrations).
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    location = Column(String(255), nullable=False)
    floor = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)
    # Store as plain VARCHAR so legacy/typo values from DB do not break ORM loads;
    # validate with Pydantic (TenantType / TenantStatus) at API boundaries.
    tenant_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=TenantStatus.VACANT.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
