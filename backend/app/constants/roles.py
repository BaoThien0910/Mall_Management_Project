# File: app/constants/roles.py
from enum import Enum


class RoleCode(Enum):
    """Mã vai trò chuẩn dùng xuyên suốt toàn hệ thống."""

    QTV = "QTV"
    BQL = "BQL"
    TP_KDTC = "TP_KDTC"
    NV_KDTC = "NV_KDTC"
    TP_VHBT = "TP_VHBT"
    NV_VHBT = "NV_VHBT"
    KHACH_THUE = "KHACH_THUE"


INTERNAL_STAFF_ROLES = {
    RoleCode.QTV,
    RoleCode.BQL,
    RoleCode.TP_KDTC,
    RoleCode.NV_KDTC,
    RoleCode.TP_VHBT,
    RoleCode.NV_VHBT,
}

KDTC_ROLES = {
    RoleCode.TP_KDTC,
    RoleCode.NV_KDTC,
}

VHBT_ROLES = {
    RoleCode.TP_VHBT,
    RoleCode.NV_VHBT,
}

MANAGER_ROLES = {
    RoleCode.BQL,
    RoleCode.TP_KDTC,
    RoleCode.TP_VHBT,
}

ACCOUNT_ADMIN_ROLES = {
    RoleCode.QTV,
}

AUDIT_VIEW_ROLES = {
    RoleCode.QTV,
    RoleCode.BQL,
}

CONTRACT_LIST_VIEW_ROLES = {
    RoleCode.BQL,
    RoleCode.TP_KDTC,
    RoleCode.NV_KDTC,
}

PREMISE_VIEW_ROLES = {
    RoleCode.BQL,
    RoleCode.TP_VHBT,
    RoleCode.NV_VHBT,
    RoleCode.KHACH_THUE,
}
