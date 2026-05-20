# File: app/constants/statuses.py
from enum import Enum


class MatBangStatus(Enum):
    """Trạng thái vận hành của mặt bằng."""

    CON_TRONG = "Còn trống"
    DANG_THUE = "Đang thuê"
    DANG_BAO_TRI = "Đang bảo trì"


class HopDongStatus(Enum):
    """Trạng thái vòng đời của hợp đồng thuê."""

    DANG_HIEU_LUC = "Đang hiệu lực"
    HET_HAN = "Hết hạn"
    DA_HUY = "Đã hủy"


class YeuCauThueThemStatus(Enum):
    """Trạng thái xử lý yêu cầu thuê thêm mặt bằng."""

    CHO_DUYET = "Chờ duyệt"
    DA_DUYET_CHO_SO_HOA_HOP_DONG = "Đã duyệt - Chờ số hóa hợp đồng"
    TU_CHOI = "Từ chối"
    DA_TAO_HOP_DONG = "Đã tạo hợp đồng"


class SuCoBaoTriStatus(Enum):
    """Trạng thái xử lý sự cố bảo trì."""

    CHO_DUYET = "Chờ duyệt"
    DA_DUYET = "Đã duyệt"
    TU_CHOI = "Từ chối"
    DANG_XU_LY = "Đang xử lý"
    HOAN_THANH = "Hoàn thành"


class LichBaoTriStatus(Enum):
    """Trạng thái thực hiện lịch bảo trì."""

    CHUA_THUC_HIEN = "Chưa thực hiện"
    DANG_THUC_HIEN = "Đang thực hiện"
    HOAN_THANH = "Hoàn thành"
    HUY = "Hủy"


class CongNoStatus(Enum):
    """Trạng thái thanh toán của công nợ."""

    CHUA_THANH_TOAN = "Chưa thanh toán"
    DA_THANH_TOAN = "Đã thanh toán"
    QUA_HAN = "Quá hạn"


class HoaDonStatus(Enum):
    """Trạng thái xử lý hóa đơn hoặc giao dịch thanh toán."""

    DANG_XU_LY = "Đang xử lý"
    THANH_CONG = "Thành công"
    THAT_BAI = "Thất bại"


class BaoCaoTaiChinhStatus(Enum):
    """Trạng thái phát hành của báo cáo tài chính."""

    BAN_NHAP = "Bản nháp"
    DA_BAN_HANH = "Đã ban hành"


class ThongBaoStatus(Enum):
    """Trạng thái phát hành của thông báo."""

    DA_BAN_HANH = "Đã ban hành"
    DA_THU_HOI = "Đã thu hồi"


class DuLieuImportTaiChinhStatus(Enum):
    """Trạng thái xử lý dữ liệu import tài chính."""

    HOP_LE = "Hợp lệ"
    LOI = "Lỗi"
    DA_DUNG_TINH_CONG_NO = "Đã dùng tính công nợ"


class PhuongThucThanhToan(Enum):
    """Phương thức thanh toán mô phỏng trong hệ thống."""

    VNPAY = "VNPay"
    MOMO = "MoMo"
    ZALOPAY = "ZaloPay"


class LoaiBaoCaoTaiChinh(Enum):
    """Loại báo cáo tài chính được hỗ trợ."""

    BAO_CAO_CONG_NO = "Báo cáo công nợ"
    BAO_CAO_DOANH_SO = "Báo cáo doanh số"


class LoaiThongBao(Enum):
    """Loại thông báo có thể ban hành."""

    THONG_BAO = "Thông báo"
    KE_HOACH = "Kế hoạch"
    QUY_DINH = "Quy định"


class DoiTuongNhanThongBao(Enum):
    """Nhóm người nhận thông báo."""

    TOAN_HE_THONG = "Toàn hệ thống"
    NOI_BO = "Nội bộ"
    KHACH_THUE = "Khách thuê"


class LoaiKhoanTaiChinh(Enum):
    """Loại khoản mục tài chính có thể import."""

    TIEN_THUE = "Tiền thuê"
    TIEN_DIEN = "Tiền điện"
    TIEN_NUOC = "Tiền nước"
    PHI_BAO_TRI = "Phí bảo trì"
    HOAN_TRA = "Hoàn trả"


class AuditAction(Enum):
    """Nhóm hành động được ghi nhận trong nhật ký thao tác."""

    DANG_NHAP = "Đăng nhập"
    DANG_XUAT = "Đăng xuất"
    TAO_MOI = "Tạo mới"
    CAP_NHAT = "Cập nhật"
    XOA = "Xóa"
    DUYET = "Duyệt"
    VUOT_QUYEN = "Vượt quyền"
