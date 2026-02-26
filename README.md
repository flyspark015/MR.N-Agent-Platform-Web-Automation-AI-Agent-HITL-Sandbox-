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

## Human Test (Fresh Machine Setup)

### Requirements

- Python 3.12+ recommended (3.11+ ok)
- Playwright Chromium
- OpenAI API key

### Windows PowerShell Setup

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python -m apps.cli.main
```

### Windows: Run MR.N by typing `mrn`

```
.\scripts\install_windows.ps1
```

Open a new PowerShell window and run:

```
mrn
```

### macOS/Linux Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
python -m apps.cli.main
```

### Smoke Test

```
python scripts/smoke_test.py
```

Expected:
- `discover_sources` returns >=3 non-Google URLs
- Playwright opens `example.com` and title contains ?Example?
- Report written to `data/smoke/smoke_<ts>.json`

## Source Discovery Reliability (R3.4)

- Provider chain with fallbacks (Google best-effort + DuckDuckGo HTML)
- Organic results only (no ads, no Google or DuckDuckGo properties)
- Failsafe query refinements when results are thin
- Ranked by credibility heuristics
- Debug artifacts saved on provider failure in `data/run_<id>/research/debug/`
- Artifact: `<provider>_last_url.txt`
- Artifact: `<provider>_html_snippet.txt`

Run the discovery benchmark:

```
python -m benchmarks.discovery_suite
```

Or in the CLI:

```
/bench discovery
```

Target success rate: >= 80% goals with >= 4 unique non-Google domains.

## Takeover Rules (Required)

The agent pauses and requests manual takeover for:

- Login flows
- OTP / CAPTCHA
- Payments
- Sending messages/emails
- Delete/cancel actions
- Account setting changes

The agent does **not** attempt to bypass CAPTCHA/OTP.

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

## Troubleshooting

- **Missing API key**: set `OPENAI_API_KEY` in `.env`
- **Playwright dependency errors**: run `python -m playwright install chromium`
- **Screenshots not saved**: verify `./data/run_<id>/screenshots` exists and is writable
