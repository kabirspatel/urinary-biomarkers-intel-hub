import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root (parent of /app)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select
from db.session import db_session
from db.models import Item
from services.auth.access import require_login

require_login()
st.title("Patents Radar (Private)")

days = st.slider("Days", 1, 365, 90)
cutoff = datetime.utcnow() - timedelta(days=int(days))

with db_session() as s:
    rows = s.execute(
        select(Item).where(Item.item_type=="patent", Item.fetched_at>=cutoff)
        .order_by(Item.published_at.desc().nullslast(), Item.fetched_at.desc())
        .limit(300)
    ).scalars().all()

df = pd.DataFrame([{
    "Published": r.published_at,
    "Publication": r.summary,
    "Title": r.title,
    "Assignee (approx)": r.company,
    "Link": r.url,
} for r in rows])

st.dataframe(df, use_container_width=True, hide_index=True)
st.caption("For production: add CPC tags + top assignees + 'citation velocity'.")
