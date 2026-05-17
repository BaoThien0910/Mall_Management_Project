"""Stub — sau nối middleware ghi AuditLog vào DB."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.database import SessionLocal
from app.config import get_settings
from app.services.audit_service import log_action

settings = get_settings()

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        
        # Mở session database riêng cho tầng middleware
        db = SessionLocal()
        
        # Thử lấy mã tài khoản (MATK) từ JWT Token nếu người dùng đã đăng nhập
        ma_tk = "GUEST" 
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                # Giả định payload lưu định danh tài khoản ở trường 'sub' hoặc bạn có thể map lại
                ma_tk = payload.get("sub", "UNKNOWN")
            except JWTError:
                pass

        # Lấy địa chỉ IP của Client gửi request lên
        ip_address = request.client.host if request.client else "127.0.0.1"

        # Bản đồ ánh xạ phương thức HTTP sang chữ tiếng Việt tương ứng với CHECK CONSTRAINT
        method_mapping = {
            "POST": "Tạo mới",
            "PUT": "Cập nhật",
            "PATCH": "Cập nhật",
            "DELETE": "Xóa"
        }

        # Thực thi API chính thức
        response = await call_next(request)

        # Chỉ ghi nhật ký tự động nếu API chạy thành công (2xx) và là các hành động thay đổi dữ liệu
        if response.status_code >= 200 and response.status_code < 300:
            if method in method_mapping:
                hanh_dong_vn = method_mapping[method]
                
                # Phân tích sơ bộ đối tượng dựa trên đường dẫn URL
                # Ví dụ: /premises -> Mặt bằng, /contracts -> Hợp đồng
                doi_tuong_uoc_tinh = "Hệ thống"
                if "/premises" in path:
                    doi_tuong_uoc_tinh = "Mặt bằng"
                elif "/contracts" in path:
                    doi_tuong_uoc_tinh = "Hợp đồng"
                elif "/finance" in path:
                    doi_tuong_uoc_tinh = "Tài chính/Công nợ"

                # Gọi service ghi nhận nhật ký tự động vào SQL Server
                log_action(
                    db=db,
                    ma_tk=ma_tk,
                    hanh_dong=hanh_dong_vn,
                    doi_tuong=doi_tuong_uoc_tinh,
                    chi_tiet=f"Người dùng gọi API {method} {path}",
                    ip_address=ip_address
                )

        db.close()
        return response