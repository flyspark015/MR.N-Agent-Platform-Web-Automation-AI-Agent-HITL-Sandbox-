# MR.N Local Agent

Local, single-user AI web automation agent that runs on localhost. No accounts, no multi-user, no SaaS, no cloud deployment.

## Project Purpose (Current Scope)

- Local AI web automation agent
- Runs on `localhost`
- Uses user-provided `OPENAI_API_KEY`
- No accounts, no multi-user, no RBAC, no cloud infrastructure

## Architecture (Phase 3)

- **API**: FastAPI (`apps/api`) for planning + dispatching
- **Worker**: Playwright Chromium headless (`apps/worker`) for navigation + screenshots
- **UI**: Next.js (`apps/ui`) for task input and results
- **Local storage**:
  - `./data/screenshots` (current)
  - `./data/results` (future)
  - `./data/traces` (future)

**Text diagram**

User ? UI ? API ? Worker ? Browser ? Screenshot ? UI

## Phase 3 Capability (What Works Today)

- Planner creates a `NAVIGATE` step
- Worker launches Chromium (headless)
- Navigates to URL
- Captures screenshot
- Returns:
  - final URL
  - page title
  - status
- UI displays screenshot + metadata

## Features

- Local planning endpoint
- Playwright navigation + screenshot capture
- UI to run a task and view results

## Getting Started

### Prerequisites

- Docker Desktop installed and running
- OpenAI API key

### First Run / Setup

**Current behavior**: this project reads the API key from `.env`. It does **not** prompt you yet.

1. Copy `.env.example` to `.env`
2. Set the key:

```
OPENAI_API_KEY=your_key_here
```

**Key storage**: `.env` file in the repo root.

**Reset**: delete `.env` or clear `OPENAI_API_KEY` and re-run.

> Note: When a CLI prompt is added in a future phase, it should only ask once and store the key so it is not requested again unless the key is removed.

### Run (Docker)

```
docker compose -f infra/docker-compose.yml up --build
```

Open:

```
http://localhost:3000
```

Test task:

```
Open https://example.com
```

Expected result:

- Screenshot appears in the UI
- File saved to `./data/screenshots/{task_id}_{step_id}.png`

## Current Capabilities

- Only `NAVIGATE` is executed end-to-end
- Results include screenshot, final URL, and page title

## Next Phase

- Add screenshots + traces per step (Phase 4)
- Add extraction and results view (Phase 5/6)
- Add takeover mode (Phase 7)

## Localhost Test

### Quick Start (Minimal)

```
docker compose -f infra/docker-compose.yml up --build
```

Then in another terminal:

```
curl http://localhost:8000/health
```

### Full Local Tests (Manual)

These commands validate each app layer. Some steps may fail if you do not have local Node/Python installed and prefer Docker-only workflows.

UI:

```
cd apps/ui
npm install
npm run build
npm run lint
```

API:

```
cd apps/api
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Worker:

```
cd apps/worker
pip install -r requirements.txt
python -m playwright install --with-deps chromium
python main.py
```

Smoke test (API):

```
curl http://localhost:8000/health
```

Planner test:

```
curl -X POST http://localhost:8000/plan -H "Content-Type: application/json" -d "{\"task\":\"Open https://example.com\"}"
```

Run test (end-to-end):

```
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d "{\"task\":\"Open https://example.com\"}"
```

Expected results:

- `/health` returns `{"status":"ok"}`
- `/plan` returns a JSON plan with a `NAVIGATE` step
- `/run` returns a plan with `status=COMPLETED` and a `screenshot_url`
- UI renders the screenshot and metadata

How to interpret failures:

- `OPENAI_API_KEY is not set`: missing `.env`
- `Planner failed`: key invalid, model not available, or OpenAI request failed
- `Navigate failed`: Playwright missing dependencies or Chromium not installed
- `Connection refused`: API or worker not running / ports blocked

> If you are using Codex to validate, ask it to run the commands above and report PASS/FAIL with errors and fixes.

## Troubleshooting

- **Missing API key**: set `OPENAI_API_KEY` in `.env`
- **Port in use**: stop the process using ports `3000`, `8000`, or `8001`
- **Node/Python mismatch**: use Node 20 and Python 3.11 (matching Dockerfiles)
- **Playwright dependency errors**: run `python -m playwright install --with-deps chromium` inside the worker container or locally
- **Screenshots not saved**: verify `./data/screenshots` exists and is mounted into the worker container
