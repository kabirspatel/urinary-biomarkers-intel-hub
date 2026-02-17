import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (parent of /app)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import select, func
from db.session import db_session
from db.models import Item

from db.bootstrap import ensure_tables
ensure_tables()

st.title("Executive Overview")

def kpi(item_type: str, days: int):
    cutoff = datetime.utcnow() - timedelta(days=days)
    with db_session() as s:
        stmt = select(func.count()).select_from(Item).where(Item.item_type==item_type, Item.fetched_at>=cutoff)
        return s.execute(stmt).scalar_one()

cols = st.columns(4)
cols[0].metric("New biomarker papers (30d)", kpi("paper", 30))
cols[1].metric("New device items (30d)", kpi("device", 30))
cols[2].metric("New patents (30d)", kpi("patent", 30))
cols[3].metric("News items (30d)", kpi("news", 30))

st.info("Next: add tagging during ingest (disease/analyte/modality/company) to power trend tiles.")
