from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    kind: Mapped[str] = mapped_column(String(50))  # rss / api / manual
    homepage: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Item(Base):
    """Generic feed item: news / paper / patent / device. Store metadata + link."""
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    item_type: Mapped[str] = mapped_column(String(30))  # news/paper/patent/device

    title: Mapped[str] = mapped_column(String(700))
    url: Mapped[str] = mapped_column(String(1200))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # light tags for MVP
    disease_area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    analyte_class: Mapped[str | None] = mapped_column(String(60), nullable=True)
    modality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)

    source: Mapped["Source"] = relationship()

    __table_args__ = (
        UniqueConstraint("source_id", "url", name="uq_source_url"),
    )

class WatchRule(Base):
    __tablename__ = "watch_rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    query: Mapped[str] = mapped_column(String(1000))  # MVP keyword query
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
