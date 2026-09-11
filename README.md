# Intelligent Land Record Digitization — Mocked Demo (SIH PS-26018)

> **Status: ✅ Working end-to-end demo (mocked tier). Verified live in browser + curl.**

SIH 2026 hackathon-demo build. A Next.js frontend uploads a scanned land-record
image to a FastAPI backend; the backend returns a canned/randomized JSON
payload (extracted fields + confidence scores) simulating an OCR/NER
pipeline. No real OCR, no DB, no auth — the goal is a believable, working
demo of the upload → processing → results-with-confidence flow.

Full plan: `.hermes/plans/2026-09-11_land-record-mock-fe-be-contract.md`
Scoping estimate (functional-prototype tier, not built now): `.hermes/plans/2026-09-11_land-record-digitization-timeline.md`

## Progress

| Task | Status |
|---|---|
| 1. Scaffold `backend/`, `mockups/` dirs | ✅ Done |
| 2. 5 UI mockup directions | ⏭️ Skipped — went straight to a working default UI instead (clean slate/table style) |
| 3. FastAPI skeleton + `/health` | ✅ Done — verified `curl localhost:8000/health` → `{"status":"ok"}` |
| 4. Fixture data module (TDD) | ✅ Done — 3/3 tests passing |
| 5. `/api/analyze` endpoint (TDD) | ✅ Done — 2/2 tests passing (5/5 total backend tests) |
| 6. CORS for localhost:3000 | ✅ Done, included in main.py from the start |
| 7. Scaffold Next.js frontend | ✅ Done (TypeScript + Tailwind + App Router) |
| 8. Typed API client | ✅ Done — `frontend/src/lib/api.ts` |
| 9. Upload/results page | ✅ Done — `frontend/src/app/page.tsx`, verified live in real browser |

**Live verification performed this session:**
- `pytest` in `backend/`: **5 passed**
- `curl http://localhost:8000/health` → `{"status":"ok"}`
- `curl -F file=@... /api/analyze` → full JSON payload with fields/confidence
- Real browser test (upload a file via the actual page): loading spinner →
  results table → "Needs review" banner rendered correctly with live data
  from the backend (confidence badges color-coded green/amber/red).

## Structure

```
2026-09-11_SIH/
  backend/       FastAPI mock API (fixtures.py, main.py, tests) — venv included, gitignored
  frontend/      Next.js + TypeScript + Tailwind app (App Router)
    src/lib/api.ts     typed fetch client for /api/analyze
    src/app/page.tsx   upload -> loading -> results UI
  mockups/       (reserved — design comparison pages, not built; skipped this pass)
  IDEA.md        Original one-line idea pointer
  README.md      This file
```

## Contract (frontend <-> backend)

`POST http://localhost:8000/api/analyze` (multipart `file=`) → JSON with
`fields[]` (khata_no, khasra_no, survey_no, owner_name, area, mutation),
`overall_confidence`, `review_required` (true if any field confidence < 0.7).
Simulated latency 1.2–2.5s so the UI shows a real loading state.
Full contract details in the plan doc above.

## Running locally

```bash
# backend (port 8000)
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# run backend tests
pytest -v

# frontend (port 3000)
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`, upload any image file, watch the ~1.2–2.5s
processing state, then see 6 extracted fields with confidence badges.

## What's deliberately NOT built (out of scope for this tier)

- Real OCR/NER — `backend/fixtures.py` hashes the filename to deterministically
  pick one of 3 canned field-sets. Same filename = same result every time.
- Database, auth, GIS/map layer, review-correction workflow.
- The 5 alternate UI mockup directions from the original plan — one clean
  default UI was built directly instead to get to a working demo fastest.

See `.hermes/plans/2026-09-11_land-record-digitization-timeline.md` for what
a real functional-prototype build (real OCR+NER, Postgres+PostGIS, auth,
GIS) would actually take (~27–44 hrs across 1.5–3 weeks, gated on you
supplying real sample scans and picking a target script/language).

## Next steps (your call)

1. Demo this as-is for SIH pitch/round 1 — it's fully functional right now.
2. If you want the 5 UI mockup directions to choose a different visual
   style, say so and I'll generate them.
3. If SIH wants a real pipeline next round, we scope Phase 0 (sample scans +
   target script) from the timeline plan.
