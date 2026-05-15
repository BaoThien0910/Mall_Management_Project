from enum import Enum
import unicodedata


class TenantType(str, Enum):
    STORE = "Cửa hàng"
    OFFICE = "Văn phòng"
    RESTAURANT = "Nhà hàng"
    OTHER = "Khác"


# Legacy / typo DB values -> canonical enum string (same as member.value)
# "C?a hàng": VARCHAR / encoding loss — "ử" in "Cửa hàng" became "?" or U+FFFD.
TENANT_TYPE_STRING_ALIASES: dict[str, str] = {
    "Van phòng": TenantType.OFFICE.value,
    "C?a hàng": TenantType.STORE.value,
    "C\ufffda hàng": TenantType.STORE.value,
}


def canonical_tenant_type_string(raw: str) -> str:
    mapped = TENANT_TYPE_STRING_ALIASES.get(raw)
    if mapped is not None:
        return mapped
    s = raw
    store = TenantType.STORE.value
    if len(s) == len(store) and s.startswith("C") and s[2:] == store[2:] and s[1] in ("?", "\ufffd"):
        return store
    return s


def parse_tenant_type(raw: object) -> TenantType:
    if isinstance(raw, TenantType):
        return raw
    if not isinstance(raw, str):
        raise TypeError("tenant_type must be str or TenantType")
    s = canonical_tenant_type_string(raw)
    try:
        return TenantType(s)
    except ValueError:
        n = unicodedata.normalize("NFC", s)
        for m in TenantType:
            if unicodedata.normalize("NFC", m.value) == n:
                return m
        raise ValueError(f"Unknown tenant type: {raw!r}") from None


class TenantStatus(str, Enum):
    VACANT = "Còn trống"
    OCCUPIED = "Đang thuê"
    MAINTENANCE = "Đang bảo trì"


# Wrong first letter: U+00D0 (Ð) instead of U+0110 (Đ); common mojibake in DB / imports.
# "Còn tr?ng": UTF-8 / VARCHAR corruption where "ố" became "?" or U+FFFD.
TENANT_STATUS_STRING_ALIASES: dict[str, str] = {
    "\u00d0" + TenantStatus.OCCUPIED.value[1:]: TenantStatus.OCCUPIED.value,
    "\u00d0" + TenantStatus.MAINTENANCE.value[1:]: TenantStatus.MAINTENANCE.value,
    "Còn tr?ng": TenantStatus.VACANT.value,
    "Còn tr\ufffdng": TenantStatus.VACANT.value,
}


def canonical_tenant_status_string(raw: str) -> str:
    s = raw
    # "Còn trống" with lost combining vowel (SQL VARCHAR / bad client encoding)
    if s.startswith("Còn tr") and s.endswith("ng"):
        inner = s[len("Còn tr") : -len("ng")]
        if inner != "ố" and (not inner or set(inner) <= {"?", "\ufffd"}):
            s = TenantStatus.VACANT.value
    # U+00D0 (Ð) instead of U+0110 (Đ) at start of "Đang …"
    if s.startswith("\u00d0ang"):
        s = "\u0110" + s[1:]
    # "ả" (U+1EA3) in "bảo" often becomes ASCII "?" when encoding is wrong
    s = s.replace("b?o", "b\u1ea3o")
    s = s.replace("b\ufffdo", "b\u1ea3o")
    mapped = TENANT_STATUS_STRING_ALIASES.get(s)
    if mapped is not None:
        return mapped
    return s


def parse_tenant_status(raw: object) -> TenantStatus:
    if isinstance(raw, TenantStatus):
        return raw
    if not isinstance(raw, str):
        raise TypeError("status must be str or TenantStatus")
    s = canonical_tenant_status_string(raw)
    try:
        return TenantStatus(s)
    except ValueError:
        n = unicodedata.normalize("NFC", s)
        for m in TenantStatus:
            if unicodedata.normalize("NFC", m.value) == n:
                return m
        raise ValueError(f"Unknown tenant status: {raw!r}") from None


class OperationType(str, Enum):
    CREATE = "Thêm"
    UPDATE = "Sửa"
    DELETE = "Xóa"


class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    TENANT = "tenant"