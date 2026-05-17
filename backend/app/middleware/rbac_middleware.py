"""Stub — kiểm tra quyền chi tiết tại Depends.require_*"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # 1. Bỏ qua kiểm tra đối với các Tuyến đường Công khai (Public Routes)
        public_prefixes = ["/auth/login", "/docs", "/openapi.json", "/redoc", "/"]
        if any(path.startswith(p) for p in public_prefixes) or method == "OPTIONS":
            return await call_next(request)

        # 2. KIỂM TRA PHÂN QUYỀN VĨ MÔ (Macro-level RBAC) THEO TIỀN TỐ URL
        # Đọc nhanh token từ Header để biết vai trò (Role) mà không cần chọc vào DB nhằm tối ưu tốc độ
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Thiếu mã xác thực (Token).", "data": None}
            )

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_role = payload.get("role")
            
            # --- LUẬT CHẶN CẤP CAO ---
            # Nếu đường dẫn vào phân hệ hệ thống (/system) mà không phải admin hoặc ban quản lý -> CHẶN NGAY
            if path.startswith("/system") and user_role not in ["admin", "management"]:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"success": False, "message": "Khu vực giới hạn. Vai trò của bạn không được phép truy cập!", "data": None}
                )
                
            # Nếu Khách thuê (tenant) cố tình gọi các API liên quan đến tài chính tổng hoặc bảo trì hệ thống của phòng ban khác
            if path.startswith("/finance/import") and user_role == "tenant":
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"success": False, "message": "Bạn không có quyền thực hiện chức năng import tài chính.", "data": None}
                )

        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Mã xác thực không hợp lệ hoặc đã hết hạn.", "data": None}
            )

        # Nếu vượt qua tất cả các chốt chặn vĩ mô, cho phép request đi tiếp vào API xử lý
        return await call_next(request)