from __future__ import annotations
"""PubMed E-utilities ingestion (metadata only)."""
import requests
from datetime import datetime
from dateutil import parser as dtparser
from sqlalchemy.orm import Session
from db.models import Source, Item

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def pubmed_search(term: str, retmax: int = 20):
    r = requests.get(ESEARCH, params={"db":"pubmed","term":term,"retmode":"json","retmax":retmax}, timeout=30)
    r.raise_for_status()
    return r.json()["esearchresult"]["idlist"]

def pubmed_summaries(ids: list[str]):
    if not ids:
        return []
    r = requests.get(ESUMMARY, params={"db":"pubmed","id":",".join(ids),"retmode":"json"}, timeout=30)
    r.raise_for_status()
    j = r.json()["result"]
    out = []
    for pid in ids:
        doc = j.get(pid)
        if not doc:
            continue
        out.append({
            "title": doc.get("title",""),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            "pubdate": doc.get("pubdate"),
            "source": doc.get("source"),
        })
    return out

def upsert_pubmed(session: Session, source_name: str, term: str, item_type: str="paper", limit: int = 20):
    source = session.query(Source).filter(Source.name == source_name).first()
    if not source:
        source = Source(name=source_name, kind="api", homepage="https://eutils.ncbi.nlm.nih.gov/")
        session.add(source)
        session.commit()

    ids = pubmed_search(term, retmax=limit)
    docs = pubmed_summaries(ids)

    inserted = 0
    for d in docs:
        title = (d["title"] or "")[:700]
        url = d["url"][:1200]
        if session.query(Item).filter(Item.source_id==source.id, Item.url==url).first():
            continue

        published_at = None
        if d.get("pubdate"):
            try:
                published_at = dtparser.parse(d["pubdate"])
            except Exception:
                published_at = None

        session.add(Item(
            source_id=source.id,
            item_type=item_type,
            title=title,
            url=url,
            summary=d.get("source"),
            published_at=published_at,
            fetched_at=datetime.utcnow(),
        ))
        inserted += 1

    session.commit()
    return inserted
