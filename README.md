# MR.N CLI Agent

Local, single-user AI web automation agent that runs on localhost. No accounts, no multi-user, no SaaS, no cloud deployment.

## Project Purpose (Current Scope)

- Local AI web automation agent
- Runs on `localhost` via terminal (CLI-only)
- Uses user-provided `OPENAI_API_KEY`
- No accounts, no multi-user, no RBAC, no cloud infrastructure

## Architecture (Phase 3+ CLI)

- **CLI**: Rich-based TUI (`apps/cli`) for goals, progress, and logs
- **Agent**: Planner + executor (`agent/`)
- **Browser**: Playwright Chromium (`browser/`)
- **Storage**: Local filesystem (`storage/`)
- **Logs**: Structured logs + optional JSONL (`logs/`)
- **Local storage**:
  - `./data/screenshots` (current)
  - `./data/results` (current)
  - `./data/traces` (optional)
  - `./data/logs` (optional)

**Text diagram**

User ? CLI ? Planner ? Executor ? Playwright ? Screenshot/Results ? CLI

## Phase 3 Capability (What Works Today)

- Planner creates a `NAVIGATE` step
- Worker launches Chromium (headed by default)
- Navigates to URL
- Captures screenshot
- Returns:
  - final URL
  - page title
  - status
- CLI displays screenshot path + metadata

## Features

- Local planning endpoint (OpenAI via `OPENAI_API_KEY`)
- Playwright navigation + screenshot capture
- CLI/TUI with live steps and logs

## Getting Started

### Prerequisites

- Python 3.11 recommended
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

### Setup

```
python -m venv .venv
```

Activate:

```
# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

Install:

```
pip install -r requirements.txt
python -m playwright install chromium
```

Run:

```
python -m apps.cli.main
```

Test goal:

```
Open https://example.com and tell me the page title
```

Expected result:

- Screenshot path printed in logs
- File saved to `./data/screenshots/{task_id}_step_1.png`
- Result saved to `./data/results/{task_id}.json`
- CLI shows final URL and title

## Current Capabilities

- `NAVIGATE` and `EXTRACT` work end-to-end
- Screenshots saved per step
- Results saved to `data/results`

## Next Phase

- Click/Type reliability
- Extraction schemas
- TUI polish + command improvements

## Localhost Test

### Quick Start (Minimal)

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python -m apps.cli.main
```

### Full Local Tests (Manual)

Planner schema validation:

```
python -c "from agent.models import Plan; Plan.model_json_schema(); print('OK')"
```

Storage paths:

```
python -c "from storage.files import ensure_dirs; ensure_dirs(); print('OK')"
```

Run the CLI:

```
python -m apps.cli.main
```

Expected results:

- Planner schema prints `OK`
- Storage setup prints `OK`
- CLI accepts `/new <goal>` and runs plan
- Screenshot saved to `data/screenshots`

How to interpret failures:

- `OPENAI_API_KEY is not set`: missing `.env`
- `Planner failed`: key invalid, model not available, or OpenAI request failed
- `Navigate failed`: Playwright missing dependencies or Chromium not installed
- `Connection refused`: Playwright could not launch (missing deps)

> If you are using Codex to validate, ask it to run the commands above and report PASS/FAIL with errors and fixes.

## Troubleshooting

- **Missing API key**: set `OPENAI_API_KEY` in `.env`
- **Port in use**: not applicable (CLI-only)
- **Node/Python mismatch**: use Python 3.11
- **Playwright dependency errors**: run `python -m playwright install chromium`
- **Screenshots not saved**: verify `./data/screenshots` exists and is writable
