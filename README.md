# Urinary Biomarkers Intelligence Hub (Starter Repo)

Starter Streamlit + Postgres + GitHub Actions project for:
- Biomarkers + devices + patents catalog
- Auto-updating news feeds (RSS)
- Auto-updating patent radar (Lens API optional)
- Private, login-gated dashboard (for I2CE Lab webpage)

This template is safe-by-default:
- Stores **metadata + canonical links** (not full-text copies)
- Prefers RSS + official APIs over scraping

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate  # mac/linux
# .venv\Scripts\activate # windows
pip install -r requirements.txt

# Option A: local sqlite (fastest)
streamlit run app/Home.py

# Option B: Postgres
python -m scripts.init_db
python -m scripts.run_ingest
streamlit run app/Home.py
```

## Secrets
Create `.streamlit/secrets.toml` (never commit). See `.streamlit/secrets.example.toml`.

## Scheduled ingestion (GitHub Actions)
`.github/workflows/ingest.yml` runs daily and writes into your DB (Postgres recommended).

## Deploy
- Streamlit Community Cloud (fast): deploy from GitHub.
- Render/Fly.io (better for paid/private): deploy with Docker + proper auth.

## Folder map
- `app/` Streamlit UI (multi-page)
- `services/` auth + billing stubs
- `ingest/` ETL connectors (RSS, PubMed, Lens)
- `scripts/` helpers (db init, run ingest)
- `db/` database models and sessions
