# File: app/constants/billing.py
from decimal import Decimal

# Đơn giá cố định theo quyết định nghiệp vụ hiện tại.
# Hạn chế này nên được ghi vào phần hướng phát triển: tách đơn giá thành bảng cấu hình theo kỳ áp dụng.
ELECTRICITY_UNIT_PRICE = Decimal("3500")
WATER_UNIT_PRICE = Decimal("2200")

# Excel import tài chính chỉ chứa các khoản tài chính do KDTC nhập.
# Tiền điện/nước được tính riêng từ chức năng nhập chỉ số điện nước.
IMPORT_ALLOWED_FINANCIAL_TYPES = {
    "Tiền thuê",
    "Phí bảo trì",
    "Hoàn trả",
}

IMPORT_FORBIDDEN_METER_TYPES = {
    "Tiền điện",
    "Tiền nước",
}
