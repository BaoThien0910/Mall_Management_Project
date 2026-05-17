"""Khởi tạo ứng dụng."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Đã sửa lại đường dẫn import chuẩn, bỏ chữ "backend."
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.exception_middleware import setup_exception_handlers
from app.middleware.rbac_middleware import RBACMiddleware

from app.bootstrap import bootstrap_db
from app.config import get_settings
from app.routers import auth, finance, maintenance, reports, notifications

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Bạn đảm bảo đã có file bootstrap.py trong thư mục app nhé
    bootstrap_db(seed=True)
    yield


def create_application() -> FastAPI:
    settings = get_settings()
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    # 1. Khai báo CORS Middleware (Nên đặt lên đầu để tránh bị lỗi CORS chặn)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Xử lý Exception
    setup_exception_handlers(app)

    # 3. Add Custom Middlewares
    # Lưu ý: FastAPI xử lý Middleware theo thứ tự từ dưới lên trên (LIFO). 
    # Do đó, AuditMiddleware khai báo sau cùng sẽ chạy đầu tiên để ghi nhận request.
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RBACMiddleware)  

    # 4. Đăng ký Routers (Đã xóa các dòng bị trùng lặp)
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
    
    # Gợi ý: Thêm prefix và tags cho các router còn lại để API docs (Swagger UI) đẹp hơn
    app.include_router(maintenance.router, prefix="/api/maintenance", tags=["maintenance"])
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
    
    return app


app = create_application()