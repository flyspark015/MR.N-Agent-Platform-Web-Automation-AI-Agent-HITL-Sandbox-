# MR.N CLI Agent

Local, single-user AI web automation agent that runs on localhost. No accounts, no multi-user, no SaaS, no cloud deployment.

## Project Purpose (Current Scope)

- Local AI web automation agent
- Runs on `localhost` via terminal (CLI-only)
- Uses user-provided `OPENAI_API_KEY`
- No accounts, no multi-user, no RBAC, no cloud infrastructure

## Architecture (MR.N v2)

- **Core runtime**: lifecycle, budgets, timeouts (`core/`)
- **Agent**: planner, decide, verifier, recovery, critic (`agent/`)
- **Browser**: session manager, perception, selectors, tools (`browser/`)
- **Skills**: tables, downloads, research (`skills/`)
- **Storage**: run artifacts (`storage/`)
- **Logs**: structured logs + JSONL (`logs/`)
- **Local storage**:
  - `./data/run_<id>/screenshots`
  - `./data/run_<id>/traces`
  - `./data/run_<id>/logs.jsonl`
  - `./data/run_<id>/result.json`
  - `./data/run_<id>/artifacts/{csv,downloads,research}`

**Text diagram**

User ? CLI ? Snapshot ? Decide ? Act ? Verify ? Recover ? Critic ? Repeat ? Results

## Capabilities (Phase 2 Loop)

- Sense/decide/act loop with snapshots
- Google search + open result actions
- Safe action selection with takeover rules
- Screenshot saved on each loop iteration
- Result JSON saved per run
- Table extraction and download detection
- Research summarizer (multi-page)

## Takeover Rules (Required)

The agent pauses and requests manual takeover for:

- Login flows
- OTP / CAPTCHA
- Payments
- Sending messages/emails
- Delete/cancel actions
- Account setting changes

The agent does **not** attempt to bypass CAPTCHA/OTP.

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
- Files saved under `./data/run_<id>/screenshots/...`
- Result saved to `./data/run_<id>/result.json`

## Action Types (Tool Boundary)

Allowed action types from the model:

- `navigate`
- `google_search`
- `open_result`
- `click`
- `type`
- `scroll`
- `wait`
- `back`
- `extract`
- `extract_table`
- `download`
- `summarize`
- `done`
- `takeover`

## Local Tests

Schema validation:

```
python -c "from agent.actions import Action; Action.model_json_schema(); print('OK')"
```

Storage paths:

```
python -c "from storage.fs import ensure_run_dirs; ensure_run_dirs('test'); print('OK')"
```

## Limitations

- Web content is untrusted; actions are conservative
- Takeover required for login/OTP/CAPTCHA/payments/sending/deleting
- No stealth or bypass techniques

## Troubleshooting

- **Missing API key**: set `OPENAI_API_KEY` in `.env`
- **Node/Python mismatch**: use Python 3.11
- **Playwright dependency errors**: run `python -m playwright install chromium`
- **Screenshots not saved**: verify `./data/run_<id>/screenshots` exists and is writable
