# File: app/main.py
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.exceptions import register_exception_handlers
from app.middleware import (
    AuditContextMiddleware,
    AuthContextMiddleware,
    RBACContextMiddleware,
)
from app.routers import (
    auth,
    taikhoan,
    rbac,
    matbang,
    hopdong,
    yc_thuethem,
    chisodiennuoc,
    congno,
    thanh_toan,
    import_taichinh,
    baocaotaichinh,
    sk_baotri,
    lichbt,
    baocaobaotri,
    thongbao,
    nhatky,
    dashboard,
)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Starlette/FastAPI thực thi middleware thêm sau ở lớp ngoài cùng.
# Thứ tự đăng ký dưới đây giúp incoming request đi theo luồng:
# AuditContextMiddleware -> AuthContextMiddleware -> RBACContextMiddleware.
app.add_middleware(RBACContextMiddleware)
app.add_middleware(AuthContextMiddleware)
app.add_middleware(AuditContextMiddleware)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(taikhoan.router, prefix=settings.API_V1_PREFIX)
app.include_router(rbac.router, prefix=settings.API_V1_PREFIX)
app.include_router(matbang.router, prefix=settings.API_V1_PREFIX)
app.include_router(hopdong.router, prefix=settings.API_V1_PREFIX)
app.include_router(yc_thuethem.router, prefix=settings.API_V1_PREFIX)
app.include_router(chisodiennuoc.router, prefix=settings.API_V1_PREFIX)
app.include_router(congno.router, prefix=settings.API_V1_PREFIX)
app.include_router(thanh_toan.router, prefix=settings.API_V1_PREFIX)
app.include_router(import_taichinh.router, prefix=settings.API_V1_PREFIX)
app.include_router(baocaotaichinh.router, prefix=settings.API_V1_PREFIX)
app.include_router(sk_baotri.router, prefix=settings.API_V1_PREFIX)
app.include_router(lichbt.router, prefix=settings.API_V1_PREFIX)
app.include_router(baocaobaotri.router, prefix=settings.API_V1_PREFIX)
app.include_router(thongbao.router, prefix=settings.API_V1_PREFIX)
app.include_router(nhatky.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root() -> Dict[str, str]:
    """Endpoint gốc kiểm tra ứng dụng đang hoạt động."""
    return {
        "message": "Trung tâm thương mại API đang hoạt động",
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check cơ bản của ứng dụng."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
