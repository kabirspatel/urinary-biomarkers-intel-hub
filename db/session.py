from __future__ import annotations
import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url() -> str:
    if "DATABASE_URL" in st.secrets:
        return st.secrets["DATABASE_URL"]
    return os.environ.get("DATABASE_URL", "sqlite:///local.db")

def get_engine():
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        connect_args={"prepare_threshold": 0},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def db_session():
    return SessionLocal()
