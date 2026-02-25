# MR.N CLI Agent

Local, single-user AI web automation agent that runs on localhost. No accounts, no multi-user, no SaaS, no cloud deployment.

## Project Purpose (Current Scope)

- Local AI web automation agent
- Runs on `localhost` via terminal (CLI-only)
- Uses user-provided `OPENAI_API_KEY`
- No accounts, no multi-user, no RBAC, no cloud infrastructure

## Architecture (Phase 2: Sense ? Decide ? Act)

- **CLI**: Rich-based TUI (`apps/cli`) for goals, progress, and logs
- **Agent**: Decision loop + safety policies (`agent/`)
- **Browser**: Playwright Chromium (`browser/`)
- **Storage**: Local filesystem (`storage/`)
- **Logs**: Structured logs + optional JSONL (`logs/`)
- **Local storage**:
  - `./data/screenshots` (current)
  - `./data/results` (current)
  - `./data/traces` (optional)
  - `./data/logs` (optional)

**Text diagram**

User ? CLI ? Snapshot ? Decide ? Act ? Verify ? Repeat ? Results

## Phase 2 Capability (What Works Today)

- Sense/decide/act loop with snapshots
- Google search action (`google_search`)
- Safe action selection with takeover rules
- Screenshot saved on each loop iteration
- Result JSON saved to `data/results`

## Takeover Rules (Required)

The agent pauses and requests manual takeover for:

- Login flows
- OTP / CAPTCHA
- Payments
- Sending messages/emails
- Delete/cancel actions
- Account setting changes

The agent does **not** attempt to bypass CAPTCHA/OTP.

## Features

- Local decision loop with safe actions
- Playwright navigation + screenshots
- CLI/TUI with live actions and logs

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

Test goals:

- `Open https://example.com and tell me the page title`
- `Search Google for OpenAI official site and open it`
- `Search Google for cats and extract top 3 result titles + URLs`

Expected result:

- Screenshot paths printed in logs
- Files saved to `./data/screenshots/...`
- Result saved to `./data/results/{task_id}.json`

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
python -c "from agent.actions import Action; Action.model_json_schema(); print('OK')"
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

- Schema prints `OK`
- Storage setup prints `OK`
- CLI accepts `/new <goal>` and runs the loop
- Screenshots saved to `data/screenshots`

How to interpret failures:

- `OPENAI_API_KEY is not set`: missing `.env`
- `Planner failed`: key invalid or OpenAI request failed
- `Navigate failed`: Playwright missing dependencies or Chromium not installed
- `Connection refused`: Playwright could not launch (missing deps)

## Limitations

- Web content is untrusted; actions are conservative
- Takeover required for login/OTP/CAPTCHA/payments/sending/deleting
- No stealth or bypass techniques

## Troubleshooting

- **Missing API key**: set `OPENAI_API_KEY` in `.env`
- **Port in use**: not applicable (CLI-only)
- **Node/Python mismatch**: use Python 3.11
- **Playwright dependency errors**: run `python -m playwright install chromium`
- **Screenshots not saved**: verify `./data/screenshots` exists and is writable
