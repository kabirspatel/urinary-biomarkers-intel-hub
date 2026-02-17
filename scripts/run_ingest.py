from __future__ import annotations
from sqlalchemy.orm import Session
from db.session import get_engine
from ingest.rss_ingest import upsert_rss_feed
from ingest.pubmed_ingest import upsert_pubmed

def main():
    engine = get_engine()
    with Session(engine) as s:
        inserted = 0

        inserted += upsert_rss_feed(
            s,
            source_name="PRNewswire RSS",
            feed_url="https://www.prnewswire.com/rss/news-releases-list.rss",
            item_type="news",
            limit=50,
        )

        inserted += upsert_pubmed(
            s,
            source_name="PubMed Urine Biomarkers",
            term='(urine[Title/Abstract] OR urinary[Title/Abstract]) AND (biomarker[Title/Abstract] OR cfDNA[Title/Abstract] OR exosome*[Title/Abstract])',
            item_type="paper",
            limit=25,
        )

        print(f"Inserted {inserted} new items.")

if __name__ == "__main__":
    main()
