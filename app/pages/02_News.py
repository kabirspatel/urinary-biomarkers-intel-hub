import sys
from pathlib import Path
from sqlalchemy.orm import selectinload

ROOT = Path(__file__).resolve().parents[1]  # repo root (parent of /app)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select
from db.session import db_session
from db.models import Item

#from db.bootstrap import ensure_tables
#ensure_tables()

st.title("News Module")

days = st.slider("Days", 1, 180, 30)
cutoff = datetime.utcnow() - timedelta(days=int(days))

with db_session() as s:
    rows = s.execute(
    select(Item)
    .options(selectinload(Item.source))
    .where(Item.item_type=="news", Item.fetched_at>=cutoff)
    .order_by(Item.published_at.desc().nullslast(), Item.fetched_at.desc())
    .limit(300)
).scalars().all()

df = pd.DataFrame([{
    "Published": r.published_at,
    "Title": r.title,
    "Link": r.url,
    "Source": r.source.name if r.source else "",
} for r in rows])

st.dataframe(df, use_container_width=True, hide_index=True)
