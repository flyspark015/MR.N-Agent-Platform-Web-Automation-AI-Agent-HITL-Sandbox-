from __future__ import annotations

import asyncio
from typing import Callable, Optional

from agent.extract import extract
from agent.models import Plan, Step, StepResult
from agent.policy import needs_takeover
from browser import actions
from browser.playwright_driver import PlaywrightDriver
from storage.files import screenshot_path

LogFn = Callable[[str, str], None]

async def execute_plan(
    plan: Plan,
    task_id: str,
    headless: bool,
    trace: bool,
    trace_path,
    log: LogFn,
    update_url: Callable[[str], None],
    on_takeover: Callable[[str], None],
    should_cancel: Callable[[], bool],
    should_pause: Callable[[], bool],
) -> Plan:
    driver = PlaywrightDriver(headless=headless, trace=trace, trace_path=trace_path)
    await driver.start()
    page = driver.page

    try:
        for step in plan.steps:
            if should_cancel():
                log("ERROR", "Execution cancelled")
                step.status = "FAIL"
                step.error = "Cancelled"
                break

            while should_pause():
                await asyncio.sleep(0.2)

            step.status = "RUNNING"
            step.result = StepResult()
            log("STEP", f"{step.type} #{step.id}: {step.description}")

            try:
                if step.type == "NAVIGATE":
                    url = step.params.url or ""
                    await actions.navigate(page, url)
                    step.result.final_url = page.url
                    step.result.title = await page.title()
                    update_url(page.url)
                    if await needs_takeover(page):
                        on_takeover("Login/OTP/Captcha detected")

                elif step.type == "SEARCH":
                    await actions.search(page, step.params.query or "")
                    step.result.final_url = page.url
                    step.result.title = await page.title()
                    update_url(page.url)

                elif step.type == "CLICK":
                    await actions.click(page, step.params.selector, step.params.text_hint)

                elif step.type == "TYPE":
                    await actions.type_text(
                        page,
                        step.params.selector,
                        step.params.text_hint,
                        step.params.text or "",
                    )

                elif step.type == "WAIT":
                    await actions.wait_ms(step.params.ms or 1000)

                elif step.type == "EXTRACT":
                    data = await extract(step.params.schema_name or "page_title", page)
                    step.result.extract = data
                    step.result.title = await page.title()
                    step.result.final_url = page.url

                elif step.type == "SCREENSHOT":
                    pass

                screenshot_file = screenshot_path(task_id, step.id, step.params.label)
                await actions.screenshot(page, str(screenshot_file))
                step.result.screenshot_path = str(screenshot_file)

                step.status = "DONE"
                log("EVIDENCE", f"Saved screenshot: {screenshot_file}")

            except Exception as exc:
                step.status = "FAIL"
                step.error = str(exc)
                log("ERROR", f"Step {step.id} failed: {exc}")
                if await needs_takeover(page, str(exc)):
                    on_takeover("Login/OTP/Captcha detected")
                break
    finally:
        await driver.stop()

    return plan
