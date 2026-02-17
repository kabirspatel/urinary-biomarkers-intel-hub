import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import select
from db.session import db_session
from db.models import Item

st.set_page_config(page_title="Urinary Biomarkers Intelligence Hub", layout="wide")

st.title("Urinary Biomarkers Intelligence Hub")
st.caption("MVP dashboard (metadata + links).")

colA, colB, colC = st.columns(3)
with colA:
    item_type = st.selectbox("Module", ["news","paper","patent","device"], index=0)
with colB:
    days = st.selectbox("Time window", [7, 30, 90, 365], index=1)
with colC:
    query = st.text_input("Search title", "")

cutoff = datetime.utcnow() - timedelta(days=int(days))

with db_session() as s:
    stmt = select(Item).where(Item.item_type==item_type, Item.fetched_at>=cutoff)
    if query.strip():
        stmt = stmt.where(Item.title.ilike(f"%{query.strip()}%"))
    rows = s.execute(
        stmt.order_by(Item.published_at.desc().nullslast(), Item.fetched_at.desc()).limit(200)
    ).scalars().all()

df = pd.DataFrame([{
    "Published": r.published_at,
    "Title": r.title,
    "Source": r.source.name if r.source else "",
    "Link": r.url,
} for r in rows])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Items (window)", len(df))
k2.metric("Today", int((pd.to_datetime(df["Published"]) >= (datetime.utcnow()-timedelta(days=1))).sum()) if len(df) else 0)
k3.metric("This week", int((pd.to_datetime(df["Published"]) >= (datetime.utcnow()-timedelta(days=7))).sum()) if len(df) else 0)
k4.metric("This month", int((pd.to_datetime(df["Published"]) >= (datetime.utcnow()-timedelta(days=30))).sum()) if len(df) else 0)

st.divider()

st.subheader("Feed")
if len(df)==0:
    st.info("No items yet. Run `python -m scripts.init_db` then `python -m scripts.run_ingest`.")
else:
    st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Quick chart (MVP)")
if len(df):
    d = df.copy()
    d["Day"] = pd.to_datetime(d["Published"]).dt.date
    counts = d.groupby("Day")["Title"].count().reset_index(name="Count")
    st.line_chart(counts.set_index("Day"))
