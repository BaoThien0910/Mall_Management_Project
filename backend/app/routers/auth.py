"""Auth API."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import Principal, get_principal
from app.schemas.auth import LoginBody
from app.services import auth_service
from app.utils.response import success_response  # <-- Import hàm chuẩn hóa

router = APIRouter()


@router.post("/login")
async def login(body: LoginBody, db: Session = Depends(get_db)):
    user = auth_service.authenticate_login(db, body)
    if not user:
        # Lỗi này sẽ bị file exception_middleware (lưới hứng lỗi) lúc nãy bắt lại
        # và tự động bọc thành format JSON lỗi chuẩn chỉnh cho bạn!
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai email hoặc mật khẩu!")
        
    # Lấy dữ liệu token từ service
    data_res = auth_service.build_login_response(user)
    
    # Trả về theo khuôn chuẩn
    return success_response(data=data_res, message="Đăng nhập thành công!")


@router.get("/me")
async def read_me(me: Principal = Depends(get_principal)):
    data_res = {
        "email": me.email, 
        "role": me.role, 
        "permissions": me.permissions,
        "ma_khach_dai_dien": me.ma_khach_dai_dien # Có thể thêm dòng này nếu Frontend cần hiển thị
    }
    
    # Trả về theo khuôn chuẩn
    return success_response(data=data_res, message="Lấy hồ sơ cá nhân thành công!")