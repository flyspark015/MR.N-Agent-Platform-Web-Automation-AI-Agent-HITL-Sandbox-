# Human Testing Checklist

## Setup

- Create venv
- Install requirements
- Install Playwright chromium
- Set `OPENAI_API_KEY` in `.env` or environment

## Test Goals

1. Research: "Summarize the latest FAA drone regulations"
   - Expected: `data/run_<id>/research/summary.md`

2. Research: "Compare OpenAI and Anthropic public API pricing"
   - Expected: `summary.md`, `sources.json`, `credibility.json`

3. Supplier: "Find suppliers for agricultural drone motors"
   - Expected: `supplier_intelligence.json` + `suppliers.csv`

4. Data scraping: "Extract table of GPU memory bandwidth"
   - Expected: `dataset.json` + table CSVs

5. Automation: "Apply to a newsletter form"
   - Expected: takeover prompt + `automation_proof.txt`

6. Research: "Find WHO malaria report 2023 key points"
   - Expected: research report + sources list

7. Supplier: "Find lithium battery pack manufacturers"
   - Expected: supplier dataset + sources

8. Data scraping: "Scrape ISO 9001 requirements table"
   - Expected: dataset artifacts

9. Research: "Summarize IPCC AR6 report"
   - Expected: research report + credibility

10. Automation: "Fill contact form on example site"
    - Expected: takeover + proof

## Takeover Behavior

- If login/OTP/captcha/payment/send/delete detected:
  - TUI shows takeover message
  - Browser stays open for manual completion
  - User resumes by pressing ENTER
