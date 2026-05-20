# File: app/utils/transaction.py
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy.orm import Session


@contextmanager
def transaction_context(db: Session) -> Iterator[Session]:
    """Quản lý transaction commit/rollback chuẩn cho một khối xử lý."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def commit_or_rollback(db: Session) -> None:
    """Commit session; rollback và raise lại lỗi nếu commit thất bại."""
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def refresh_instance(db: Session, instance: Any) -> Any:
    """Refresh instance từ database và trả về chính instance đó."""
    db.refresh(instance)
    return instance


def flush_or_rollback(db: Session) -> None:
    """Flush session; rollback và raise lại lỗi nếu flush thất bại."""
    try:
        db.flush()
    except Exception:
        db.rollback()
        raise
