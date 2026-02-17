from __future__ import annotations

from db.session import get_engine
from db.models import Base

def ensure_tables():
    """Create tables if they do not exist (safe to run every startup)."""
    engine = get_engine()
    Base.metadata.create_all(engine)