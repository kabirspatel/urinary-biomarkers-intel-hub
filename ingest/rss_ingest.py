from __future__ import annotations
from datetime import datetime
from dateutil import parser as dtparser
import feedparser
from sqlalchemy.orm import Session

from db.models import Source, Item

def upsert_rss_feed(session: Session, source_name: str, feed_url: str, item_type: str = "news", limit: int = 50):
    source = session.query(Source).filter(Source.name == source_name).first()
    if not source:
        source = Source(name=source_name, kind="rss", homepage=feed_url)
        session.add(source)
        session.commit()

    parsed = feedparser.parse(feed_url)
    entries = parsed.entries[:limit]

    inserted = 0
    for e in entries:
        url = getattr(e, "link", None)
        title = getattr(e, "title", None) or ""
        summary = getattr(e, "summary", None)

        published = None
        for k in ("published", "updated"):
            if getattr(e, k, None):
                try:
                    published = dtparser.parse(getattr(e, k))
                except Exception:
                    published = None
                break

        if not url or not title:
            continue

        exists = session.query(Item).filter(Item.source_id == source.id, Item.url == url).first()
        if exists:
            continue

        session.add(Item(
            source_id=source.id,
            item_type=item_type,
            title=title[:700],
            url=url[:1200],
            summary=(summary[:5000] if summary else None),
            published_at=published,
            fetched_at=datetime.utcnow(),
        ))
        inserted += 1

    session.commit()
    return inserted
