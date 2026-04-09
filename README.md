# GrandSummonersPerfect

Premium companion platform for Grand Summoners with:

- Unit and equip database with contextual filters
- Tier lists by objective and game mode
- Boss solver with mechanic-driven recommendations
- Team builder with roster-aware substitutions
- Guide hub, AI presets, and progression planner
- Admin curation workflow and ingestion pipeline

## Monorepo layout

- `frontend/` Next.js + TypeScript + Tailwind + Framer Motion
- `backend/` FastAPI + Python + seed/mock data + recommendation engine

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

## API docs

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`

## Notes

- MVP uses curated mock seeds for deterministic behavior.
- Database-ready SQL schema is provided at `backend/app/sql/schema.sql`.
- Ingestion pipeline skeleton is under `backend/app/ingestion/`.

## Verification

Run the automated MVP verification script from repository root:

```bash
bash scripts/verify_mvp.sh
```

It runs:

- backend tests (`pytest`)
- frontend production build (`next build`)
- runtime smoke checks for API and key frontend routes

## Documentation

- Implementation audit and requirement coverage: `docs/IMPLEMENTATION_AUDIT.md`
