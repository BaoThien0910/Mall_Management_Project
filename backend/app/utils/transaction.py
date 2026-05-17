from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session

@contextmanager
def transactional(db: Session) -> Generator[Session, None, None]:
    """
    Context Manager quản lý Transaction tự động cho SQLAlchemy.
    Sử dụng: 
        with transactional(db):
            # Các thao tác thêm, sửa, xóa...
    """
    try:
        # Nhường quyền cho khối code bên trong `with` chạy
        yield db
        
        # Nếu mọi thứ êm đẹp, tự động chốt dữ liệu
        db.commit()
        
    except Exception as e:
        # Nếu có BẤT KỲ lỗi gì xảy ra, lập tức quay xe (rollback)
        db.rollback()
        
        # Ném lỗi đó ra ngoài để Exception Middleware (bạn đã viết lúc nãy) 
        # bắt lấy và trả về JSON báo lỗi 500 cho Frontend.
        raise e