# Intelligent Land Record Digitization — Mocked Demo (SIH PS-26018)

> **Status: 🚧 In progress — this README is updated live as work happens.**

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
| 2. 5 UI mockup directions (pick one before Task 9) | ⏳ In progress |
| 3. FastAPI skeleton + `/health` | ⬜ Not started |
| 4. Fixture data module (TDD) | ⬜ Not started |
| 5. `/api/analyze` endpoint (TDD) | ⬜ Not started |
| 6. CORS for localhost:3000 | ⬜ Not started |
| 7. Scaffold Next.js frontend | ⬜ Not started |
| 8. Typed API client (TDD) | ⬜ Not started |
| 9. Real upload/results page (blocked on mockup choice) | ⬜ Not started |

## Structure

```
2026-09-11_SIH/
  backend/       FastAPI mock API (fixtures, /api/analyze, /health)
  mockups/       5 disposable HTML UI direction comparisons
  frontend/      Next.js + TypeScript + Tailwind app (Task 7+)
  IDEA.md        Original one-line idea pointer
  README.md      This file
```

## Contract (frontend <-> backend)

`POST http://localhost:8000/api/analyze` (multipart `file=`) → JSON with
`fields[]` (khata_no, khasra_no, survey_no, owner_name, area, mutation),
`overall_confidence`, `review_required` (true if any field confidence < 0.7).
Simulated latency 1.2–2.5s. Full contract in the plan doc above.

## Running locally (once built)

```bash
# backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# frontend
cd frontend && npm run dev
```
