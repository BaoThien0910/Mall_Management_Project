from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from math import ceil

from ..db import get_db
from ..crud import (
    get_tenant_by_id, get_tenant_by_code, get_tenants, get_tenants_count,
    create_tenant, update_tenant, delete_tenant
)
from ..schemas import Tenant, TenantCreate, TenantUpdate, TenantFilter, PaginatedTenants
from ..enums import TenantStatus

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=Tenant)
async def create_tenant_endpoint(
    tenant: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await create_tenant(db, tenant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PaginatedTenants)
async def list_tenants(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[TenantStatus] = None,
    floor: Optional[int] = None,
    tenant_type: Optional[str] = None,
    area_min: Optional[float] = Query(None, ge=0),
    area_max: Optional[float] = Query(None, ge=0),
    db: AsyncSession = Depends(get_db)
):
    # For simplicity, assuming all users are internal (not implementing full auth yet)
    # In real app, check user role here
    is_customer = False  # Set to True for customer role

    filters = TenantFilter(
        status=status,
        floor=floor,
        tenant_type=tenant_type,
        area_min=area_min,
        area_max=area_max
    )

    if is_customer:
        # Customers only see vacant tenants
        filters.status = TenantStatus.VACANT

    skip = (page - 1) * size
    tenants = await get_tenants(db, skip=skip, limit=size, filters=filters)
    total = await get_tenants_count(db, filters=filters)
    total_pages = ceil(total / size)

    return PaginatedTenants(
        items=tenants,
        total=total,
        page=page,
        size=size
    )


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    tenant = await get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Mặt bằng không tồn tại")
    return tenant


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant_endpoint(
    tenant_id: int,
    tenant_update: TenantUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await update_tenant(db, tenant_id, tenant_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tenant_id}")
async def delete_tenant_endpoint(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        await delete_tenant(db, tenant_id)
        return {"message": "Mặt bằng đã được xóa"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))