from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..db import get_db
from ..crud import (
    create_user, disable_user, enable_user, list_users, 
    get_user_by_id, authenticate_user
)
from ..schemas import User, UserCreate, UserUpdate, LoginRequest
from ..enums import UserRole

router = APIRouter(prefix="/users", tags=["users"])


def verify_admin(user: dict) -> bool:
    """Verify that the current user is an admin."""
    if not user or user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể thực hiện hành động này"
        )
    return True


@router.post("", response_model=User)
async def create_new_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = None
):
    """
    Create a new user account (admin only).
    - Admin: Can create admin, staff, and tenant accounts
    - Staff/Tenant: Cannot create accounts
    """
    # In real implementation, extract current_user from token
    # For now, we'll assume admin role. You should implement JWT token validation.
    if not current_user or current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể tạo tài khoản"
        )
    
    try:
        return await create_user(db, user_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def list_all_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = None
):
    """
    List all users (admin only).
    Can filter by role: admin, staff, tenant
    """
    # Verify admin role
    if not current_user or current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể xem danh sách tài khoản"
        )
    
    skip = (page - 1) * size
    users, total = await list_users(db, skip=skip, limit=size, role=role)
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = None
):
    """
    Get user details (admin only).
    """
    if not current_user or current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể xem chi tiết tài khoản"
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tài khoản không tồn tại"
        )
    return user


@router.put("/{user_id}/disable", response_model=User)
async def disable_user_account(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = None
):
    """
    Disable a user account (admin only).
    Cannot disable the last admin user.
    """
    if not current_user or current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể vô hiệu hóa tài khoản"
        )
    
    try:
        return await disable_user(db, user_id, current_user.get("id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}/enable", response_model=User)
async def enable_user_account(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = None
):
    """
    Enable a disabled user account (admin only).
    """
    if not current_user or current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ quản trị viên mới có thể bật lại tài khoản"
        )
    
    try:
        from ..crud import enable_user
        return await enable_user(db, user_id, current_user.get("id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
