from datetime import datetime
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session

def log_action(
    db: Session,
    ma_tk: str,
    hanh_dong: str,
    doi_tuong: str,
    ma_doi_tuong: str | None = None,
    gia_tri_cu: str | None = None,
    gia_tri_moi: str | None = None,
    chi_tiet: str | None = None,
    ip_address: str | None = None
) -> None:
    """
    Hàm toàn cục ghi nhật ký thao tác hệ thống vào bảng dbo.NHATKY.
    Ràng buộc CHECK HANHDONG: 'Đăng nhập', 'Đăng xuất', 'Tạo mới', 'Cập nhật', 'Xóa', 'Duyệt', 'Vượt quyền'
    """
    try:
        # Tự sinh mã nhật ký varchar(20), ví dụ: NK-A1B2C3D4E5
        ma_nhat_ky = f"NK-{uuid4().hex[:16].upper()}"[:20]
        
        query = text("""
            INSERT INTO dbo.NHATKY (
                MANHATKY, MATK, THOIGIAN, HANHDONG, DOITUONG, 
                MADOITUONG, GIATRICU, GIATRIMOI, CHITIET, IP_ADDRESS
            ) VALUES (
                :ma_nhat_ky, :ma_tk, :thoi_gian, :hanh_dong, :doi_tuong, 
                :ma_doi_tuong, :gia_tri_cu, :gia_tri_moi, :chi_tiet, :ip_address
            )
        """)
        
        db.execute(query, {
            "ma_nhat_ky": ma_nhat_ky,
            "ma_tk": ma_tk,
            "thoi_gian": datetime.now(),
            "hanh_dong": hanh_dong, # Phải khớp với CONSTRAINT CHECK của SQL Server
            "doi_tuong": doi_tuong,
            "ma_doi_tuong": ma_doi_tuong,
            "gia_tri_cu": gia_tri_cu,
            "gia_tri_moi": gia_tri_moi,
            "chi_tiet": chi_tiet,
            "ip_address": ip_address
        })
        db.commit()
    except Exception as e:
        db.rollback()
        # Chỉ in log debug lỗi ghi log chứ không làm sập luồng xử lý chính của người dùng
        print(f"❌ Không thể ghi Audit Log: {e}")