# File: app/constants/statuses.py
"""
Hằng số trạng thái dùng xuyên suốt hệ thống.
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
