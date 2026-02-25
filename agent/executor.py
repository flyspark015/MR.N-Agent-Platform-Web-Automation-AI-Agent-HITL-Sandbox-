from __future__ import annotations

import asyncio
from typing import Callable, List

from agent.actions import Action, ActionRecord, VerifyRule
from agent.decide import decide_action
from agent.extract import extract
from agent.policy import needs_takeover
from browser import actions
from browser.playwright_driver import PlaywrightDriver

LogFn = Callable[[str, str], None]
UpdateUrlFn = Callable[[str], None]
UpdateTitleFn = Callable[[str], None]
UpdateScreenshotFn = Callable[[str], None]
UpdateActionsFn = Callable[[List[ActionRecord]], None]

async def run_agent_loop(
    goal: str,
    task_id: str,
    headless: bool,
    trace: bool,
    trace_path,
    log: LogFn,
    update_url: UpdateUrlFn,
    update_title: UpdateTitleFn,
    update_screenshot: UpdateScreenshotFn,
    update_actions: UpdateActionsFn,
    on_takeover: Callable[[str], None],
    max_actions: int = 40,
) -> List[ActionRecord]:
    driver = PlaywrightDriver(headless=headless, trace=trace, trace_path=trace_path)
    await driver.start()
    page = driver.page

    actions_history: List[Action] = []
    records: List[ActionRecord] = []
    seen_pairs: List[tuple[str, str, str]] = []

    async def autopilot_helpers() -> None:
        await actions.dismiss_cookie_banner(page)
        await actions.close_modal(page)
        await actions.deny_prompts(page)

    async def record_snapshot(step_id: int, index: int) -> None:
        snap = await driver.get_snapshot(task_id, step_id, index)
        log("SNAPSHOT", f"{snap.url} | {snap.title} | screenshot={snap.screenshot_path}")
        update_url(snap.url)
        update_title(snap.title)
        update_screenshot(snap.screenshot_path)

    try:
        if "http" not in goal and any(word in goal.lower() for word in ["search", "find", "look up"]):
            initial = Action(type="google_search", query=goal, reason="Start with Google search")
            record = ActionRecord(index=0, action=initial)
            records.append(record)
            update_actions(records)
            log("ACTION", f"type=google_search query={goal}")
            await actions.action_google_search(page, goal)
            record.status = "DONE"
            update_actions(records)

        for idx in range(1, max_actions + 1):
            await autopilot_helpers()
            snapshot = await driver.get_snapshot(task_id, idx, 0)
            log("SNAPSHOT", f"{snapshot.url} | {snapshot.title} | screenshot={snapshot.screenshot_path}")
            update_url(snapshot.url)
            update_title(snapshot.title)
            update_screenshot(snapshot.screenshot_path)

            action = await decide_action(goal, snapshot, actions_history)
            record = ActionRecord(index=idx, action=action)
            records.append(record)
            update_actions(records)
            log("ACTION", f"type={action.type} reason={action.reason}")

            if action.type == "takeover":
                record.status = "FAIL"
                update_actions(records)
                on_takeover("Takeover requested by policy")
                break

            if action.type == "done":
                record.status = "DONE"
                update_actions(records)
                log("DONE", "Agent marked task as done")
                break

            try:
                if action.type == "navigate":
                    await actions.navigate(page, action.url or "")
                elif action.type == "google_search":
                    await actions.action_google_search(page, action.query or "")
                elif action.type == "click":
                    await actions.click(page, action.selector, action.text_hint)
                elif action.type == "type":
                    await actions.type_text(page, action.selector, action.text_hint, action.input_text or "")
                elif action.type == "scroll":
                    await page.mouse.wheel(0, action.scroll_delta or 800)
                elif action.type == "wait":
                    await actions.wait_ms(action.wait_ms or 1000)
                elif action.type == "back":
                    await page.go_back()
                elif action.type == "extract":
                    data = await extract(action.input_text or "page_title", page)
                    log("STEP", f"Extracted: {data}")
                else:
                    raise ValueError(f"Unsupported action type: {action.type}")

                verify_ok = True
                if action.verify:
                    verify_ok = await verify_action(page, action.verify)
                    log("VERIFY", "pass" if verify_ok else "fail")

                if not verify_ok:
                    await recovery_step(page, log, goal)

                record.status = "DONE"
                update_actions(records)

            except Exception as exc:
                record.status = "FAIL"
                record.error = str(exc)
                update_actions(records)
                log("ERROR", f"Action failed: {exc}")
                if await needs_takeover(page, str(exc)):
                    on_takeover("Login/OTP/Captcha detected")
                break

            next_snapshot = await driver.get_snapshot(task_id, idx, 1)
            update_title(next_snapshot.title)
            update_screenshot(next_snapshot.screenshot_path)
            seen_pairs.append((next_snapshot.screenshot_hash, next_snapshot.dom_hash, next_snapshot.url))
            if len(seen_pairs) > 3:
                seen_pairs.pop(0)
            if len(seen_pairs) == 3 and len(set(seen_pairs)) == 1:
                log("RECOVERY", "Stuck detected, running recovery")
                await recovery_step(page, log, goal)
                repeat = await driver.get_snapshot(task_id, idx, 2)
                if repeat.screenshot_hash == next_snapshot.screenshot_hash:
                    log("TAKEOVER", "Still stuck after recovery")
                    on_takeover("Stuck on page")
                    break

            actions_history.append(action)

    finally:
        await driver.stop()

    return records


async def verify_action(page, verify: VerifyRule) -> bool:
    if verify.url_contains and verify.url_contains not in page.url:
        return False
    if verify.selector_exists:
        locator = page.locator(verify.selector_exists).first
        if await locator.count() == 0:
            return False
    if verify.text_contains:
        content = await page.content()
        if verify.text_contains not in content:
            return False
    return True


async def recovery_step(page, log: LogFn, goal: str) -> None:
    log("RECOVERY", "Attempting scroll/close/back/search")
    await actions.close_modal(page)
    await actions.dismiss_cookie_banner(page)
    await page.mouse.wheel(0, 800)
    await asyncio.sleep(0.5)
    if "http" not in goal:
        await actions.action_google_search(page, goal)
