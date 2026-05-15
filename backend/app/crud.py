from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json

from .core.security import verify_password, hash_password
from .models import User, Tenant, AuditLog
from .schemas import LoginRequest, UserCreate, TenantCreate, TenantUpdate, TenantFilter
from .enums import TenantStatus, TenantType, parse_tenant_status


def _enum_to_db_str(value: object) -> object:
    if isinstance(value, (TenantType, TenantStatus)):
        return value.value
    return value


def _audit_json_from_orm(instance: object) -> str:
    """JSON snapshot of mapped columns only (excludes SQLAlchemy internal __dict__ keys)."""
    public = {k: v for k, v in instance.__dict__.items() if not k.startswith("_")}
    return json.dumps(public, default=str)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter_by(email=email))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_create.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    user = User(
        email=user_create.email,
        password_hash=hash_password(user_create.password),
        full_name=user_create.full_name,
        phone=user_create.phone,
        role=user_create.role,
        department=user_create.department,
        tenant_id=user_create.tenant_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> User | None:
    user = await get_user_by_email(db, login_data.email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(login_data.password, user.password_hash):
        return None
    return user


# Tenant CRUD
async def get_tenant_by_id(db: AsyncSession, tenant_id: int) -> Tenant | None:
    result = await db.execute(select(Tenant).filter_by(id=tenant_id))
    return result.scalars().first()


async def get_tenant_by_code(db: AsyncSession, code: str) -> Tenant | None:
    result = await db.execute(select(Tenant).filter_by(code=code))
    return result.scalars().first()


async def get_tenants(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[TenantFilter] = None
) -> List[Tenant]:
    query = select(Tenant)

    if filters:
        conditions = []
        if filters.status:
            conditions.append(Tenant.status == filters.status)
        if filters.floor is not None:
            conditions.append(Tenant.floor == filters.floor)
        if filters.tenant_type:
            conditions.append(Tenant.tenant_type == filters.tenant_type)
        if filters.area_min is not None:
            conditions.append(Tenant.area >= filters.area_min)
        if filters.area_max is not None:
            conditions.append(Tenant.area <= filters.area_max)

        if conditions:
            query = query.where(and_(*conditions))

    query = query.order_by(Tenant.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_tenants_count(db: AsyncSession, filters: Optional[TenantFilter] = None) -> int:
    query = select(Tenant)

    if filters:
        conditions = []
        if filters.status:
            conditions.append(Tenant.status == filters.status)
        if filters.floor is not None:
            conditions.append(Tenant.floor == filters.floor)
        if filters.tenant_type:
            conditions.append(Tenant.tenant_type == filters.tenant_type)
        if filters.area_min is not None:
            conditions.append(Tenant.area >= filters.area_min)
        if filters.area_max is not None:
            conditions.append(Tenant.area <= filters.area_max)

        if conditions:
            query = query.where(and_(*conditions))

    result = await db.execute(query)
    return len(result.scalars().all())


async def create_tenant(db: AsyncSession, tenant_create: TenantCreate, user_id: Optional[int] = None) -> Tenant:
    # Check unique code
    existing = await get_tenant_by_code(db, tenant_create.code)
    if existing:
        raise ValueError("Mã mặt bằng đã tồn tại")

    data = tenant_create.dict()
    data["tenant_type"] = _enum_to_db_str(data["tenant_type"])
    data["status"] = _enum_to_db_str(data["status"])
    tenant = Tenant(**data)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    # Audit log
    await create_audit_log(
        db,
        table_name="tenants",
        record_id=tenant.id,
        operation="CREATE",
        new_values=json.dumps(tenant_create.dict(), default=str),
        user_id=user_id
    )

    return tenant


async def update_tenant(
    db: AsyncSession,
    tenant_id: int,
    tenant_update: TenantUpdate,
    user_id: Optional[int] = None
) -> Tenant:
    tenant = await get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise ValueError("Mặt bằng không tồn tại")

    old_values_json = _audit_json_from_orm(tenant)
    update_data = tenant_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field in ("tenant_type", "status"):
            value = _enum_to_db_str(value)
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    # Audit log
    await create_audit_log(
        db,
        table_name="tenants",
        record_id=tenant.id,
        operation="UPDATE",
        old_values=old_values_json,
        new_values=json.dumps(update_data, default=str),
        user_id=user_id
    )

    return tenant


async def delete_tenant(db: AsyncSession, tenant_id: int, user_id: Optional[int] = None) -> None:
    tenant = await get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise ValueError("Mặt bằng không tồn tại")

    # Check if occupied
    if parse_tenant_status(tenant.status) == TenantStatus.OCCUPIED:
        raise ValueError("Không thể xóa mặt bằng đang thuê")

    old_values_json = _audit_json_from_orm(tenant)

    await db.delete(tenant)
    await db.commit()

    # Audit log
    await create_audit_log(
        db,
        table_name="tenants",
        record_id=tenant_id,
        operation="DELETE",
        old_values=old_values_json,
        user_id=user_id
    )


# Audit Log
async def create_audit_log(
    db: AsyncSession,
    table_name: str,
    record_id: int,
    operation: str,
    old_values: Optional[str] = None,
    new_values: Optional[str] = None,
    user_id: Optional[int] = None
) -> AuditLog:
    audit_log = AuditLog(
        table_name=table_name,
        record_id=record_id,
        operation=operation,
        old_values=old_values,
        new_values=new_values,
        user_id=user_id
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log


# User management functions
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter_by(id=user_id))
    return result.scalars().first()


async def disable_user(
    db: AsyncSession,
    user_id: int,
    current_user_id: int
) -> User:
    """Disable a user account. Cannot disable the last admin user."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Tài khoản không tồn tại")
    
    if user.role.value == "admin":
        # Check if this is the last admin
        result = await db.execute(
            select(User).filter(User.role == "admin", User.is_active == True)
        )
        active_admins = result.scalars().all()
        if len(active_admins) == 1:
            raise ValueError("Không thể vô hiệu hóa tài khoản quản trị viên duy nhất")
    
    # Record old value
    old_values = json.dumps({"is_active": user.is_active})
    
    # Disable user
    user.is_active = False
    db.add(user)
    await db.commit()
    
    # Create audit log
    new_values = json.dumps({"is_active": user.is_active})
    await create_audit_log(
        db,
        "users",
        user_id,
        "Vô hiệu hóa",
        old_values,
        new_values,
        current_user_id
    )
    
    await db.refresh(user)
    return user


async def enable_user(db: AsyncSession, user_id: int, current_user_id: int) -> User:
    """Enable a user account."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Tài khoản không tồn tại")
    
    old_values = json.dumps({"is_active": user.is_active})
    user.is_active = True
    db.add(user)
    await db.commit()
    
    new_values = json.dumps({"is_active": user.is_active})
    await create_audit_log(
        db,
        "users",
        user_id,
        "Bật lại",
        old_values,
        new_values,
        current_user_id
    )
    
    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    role: Optional[str] = None
) -> tuple[List[User], int]:
    """List all users with optional role filter."""
    query = select(User)
    
    if role:
        query = query.filter_by(role=role)
    
    # Get total count
    count_result = await db.execute(select(User) if not role else select(User).filter_by(role=role))
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users, total
