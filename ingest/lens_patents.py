from __future__ import annotations
"""Lens.org Patent API ingestion (metadata only). Requires LENS_API_TOKEN."""
import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Source, Item

LENS_SEARCH = "https://api.lens.org/patent/search"

def upsert_lens_patents(session: Session, source_name: str, lens_query: dict, limit: int = 25, token: str | None = None):
    token = token or os.environ.get("LENS_API_TOKEN")
    if not token:
        raise RuntimeError("Missing LENS_API_TOKEN")

    source = session.query(Source).filter(Source.name == source_name).first()
    if not source:
        source = Source(name=source_name, kind="api", homepage="https://docs.api.lens.org/")
        session.add(source)
        session.commit()

    headers = {"Authorization": f"Bearer {token}", "Content-Type":"application/json"}
    payload = {"query": lens_query, "size": limit, "include": ["title","publication_date","url","publication_number","owners"]}
    r = requests.post(LENS_SEARCH, headers=headers, json=payload, timeout=45)
    r.raise_for_status()
    data = r.json()

    inserted = 0
    for p in data.get("data", []):
        url = p.get("url") or ""
        title = (p.get("title") or "")[:700]
        if not url or not title:
            continue
        if session.query(Item).filter(Item.source_id==source.id, Item.url==url).first():
            continue

        published_at = None
        if p.get("publication_date"):
            try:
                published_at = datetime.fromisoformat(p["publication_date"].replace("Z",""))
            except Exception:
                published_at = None

        company = None
        owners = p.get("owners") or []
        if owners and isinstance(owners, list):
            company = owners[0].get("name")

        session.add(Item(
            source_id=source.id,
            item_type="patent",
            title=title,
            url=url[:1200],
            summary=(p.get("publication_number") or ""),
            published_at=published_at,
            fetched_at=datetime.utcnow(),
            company=(company[:200] if company else None),
        ))
        inserted += 1

    session.commit()
    return inserted
