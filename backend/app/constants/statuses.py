# File: app/constants/statuses.py
"""
Hằng số trạng thái dùng xuyên suốt hệ thống.
Bao gồm cả Mốc B và Mốc C.
"""

# ── Trạng thái mặt bằng ──────────────────────────────────────────────────────
class TrangThaiMatBang:
    CON_TRONG = "Còn trống"
    DANG_THUE = "Đang thuê"
    DANG_BAO_TRI = "Đang bảo trì"

    ALL = {CON_TRONG, DANG_THUE, DANG_BAO_TRI}


# ── Trạng thái hợp đồng ──────────────────────────────────────────────────────
class TrangThaiHopDong:
    DANG_HIEU_LUC = "Đang hiệu lực"
    HET_HAN = "Hết hạn"
    DA_HUY = "Đã hủy"

    ALL = {DANG_HIEU_LUC, HET_HAN, DA_HUY}


# ── Trạng thái yêu cầu thuê thêm ─────────────────────────────────────────────
class TrangThaiYeuCau:
    CHO_DUYET = "Chờ duyệt"
    DA_DUYET_CHO_SO_HOA = "Đã duyệt - Chờ số hóa hợp đồng"
    TU_CHOI = "Từ chối"
    DA_TAO_HOP_DONG = "Đã tạo hợp đồng"

    ALL = {CHO_DUYET, DA_DUYET_CHO_SO_HOA, TU_CHOI, DA_TAO_HOP_DONG}


# ── Trạng thái dòng import tài chính ─────────────────────────────────────────
class TrangThaiImport:
    HOP_LE = "Hợp lệ"
    LOI = "Lỗi"
    DA_DUNG = "Đã dùng tính công nợ"

    ALL = {HOP_LE, LOI, DA_DUNG}


# ── Loại khoản thu/chi trong import ──────────────────────────────────────────
class LoaiKhoanThu:
    TIEN_THUE = "Tiền thuê"
    TIEN_DIEN = "Tiền điện"
    TIEN_NUOC = "Tiền nước"
    PHI_BAO_TRI = "Phí bảo trì"
    HOAN_TRA = "Hoàn trả"

    ALL = {TIEN_THUE, TIEN_DIEN, TIEN_NUOC, PHI_BAO_TRI, HOAN_TRA}


# ── Trạng thái công nợ ────────────────────────────────────────────────────────
class TrangThaiCongNo:
    CHUA_THANH_TOAN = "Chưa thanh toán"
    DA_THANH_TOAN = "Đã thanh toán"
    QUA_HAN = "Quá hạn"

    ALL = {CHUA_THANH_TOAN, DA_THANH_TOAN, QUA_HAN}


# ── Trạng thái hóa đơn / giao dịch ───────────────────────────────────────────
class TrangThaiHoaDon:
    DANG_XU_LY = "Đang xử lý"
    THANH_CONG = "Thành công"
    THAT_BAI = "Thất bại"

    ALL = {DANG_XU_LY, THANH_CONG, THAT_BAI}


# ── Trạng thái báo cáo tài chính ─────────────────────────────────────────────
class TrangThaiBaoCao:
    BAN_NHAP = "Bản nháp"
    DA_BAN_HANH = "Đã ban hành"

    ALL = {BAN_NHAP, DA_BAN_HANH}


# ── Loại báo cáo tài chính ────────────────────────────────────────────────────
class LoaiBaoCao:
    CONG_NO = "Công nợ"
    DOANH_SO = "Doanh số"

    ALL = {CONG_NO, DOANH_SO}
