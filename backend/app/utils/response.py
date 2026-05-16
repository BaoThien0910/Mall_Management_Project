"""Chuẩn hóa response lỗi / thông điệp (mở rộng sau)."""


def api_message(msg: str) -> dict[str, str]:
    return {"message": msg}
