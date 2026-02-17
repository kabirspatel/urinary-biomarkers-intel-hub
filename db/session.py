from __future__ import annotations
import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url() -> str:
    """
    Priority:
    1) ENV var DATABASE_URL (GitHub Actions, local shell, etc.)
    2) Streamlit secrets DATABASE_URL (Streamlit Cloud)
    3) Fallback to local sqlite
    """
    # 1) GitHub Actions / normal env
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2) Streamlit secrets (only available when running Streamlit)
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass

    # 3) Fallback
    return "sqlite:///local.db"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            get_database_url(),
            pool_pre_ping=True,
            connect_args={"prepare_threshold": 0},
        )
    return _engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def db_session():
    return SessionLocal()
