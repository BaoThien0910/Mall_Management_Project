"""Phân quyền vai trò / mã quyền đơn giản (RBAC MVP)."""


def permissions_for_role(role: str) -> list[str]:
    return {
        "admin": ["*"],
        "staff": ["finance.read_all", "finance.import", "finance.calculate", "finance.read_own"],
        "management": ["finance.read_all", "finance.report", "finance.approve"],
        "tenant": ["finance.read_own", "finance.pay"],
    }.get(role, [])


def role_can_access_route(role: str, route_roles: tuple[str, ...]) -> bool:
    return role in route_roles or role == "admin"
