from __future__ import annotations

import asyncio
import queue
import threading
import time

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from apps.cli.controller import AgentController
from core.config import APP_NAME, APP_VERSION
from core.research_commands import cmd_research, cmd_sources, cmd_intelligence
from core.setup import ensure_env
from storage.fs import run_dir
from storage.fs import result_path

console = Console()

HELP_TEXT = """Commands:
  /new <goal>
  /research <goal>
  /sources <goal>
  /bench discovery
  /open-run <id>
  /takeover
  /stop
  /help
  exit
"""

def build_layout(controller: AgentController) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=6),
        Layout(name="body", ratio=1),
        Layout(name="input", size=3),
    )
    layout["body"].split_row(
        Layout(name="steps", ratio=1),
        Layout(name="logs", ratio=1),
    )

    with controller.state.lock:
        status = controller.state.status
        current_url = controller.state.current_url
        current_title = controller.state.current_title
        actions = controller.state.actions
        last_shot = controller.state.last_screenshot or ""
        run_id = controller.state.task_id or ""
        mode = controller.state.mode
        playbook = controller.state.playbook_type
        confidence = controller.state.playbook_confidence
        budget = controller.state.budget
        session_status = controller.state.session_status

    run_dir_path = str(run_dir(run_id)) if run_id else ""
    header = (
        f"{APP_NAME} {APP_VERSION}\n"
        f"Mode: {mode} | Playbook: {playbook} ({confidence:.0%})\n"
        f"Status: {status} | URL: {current_url}\n"
        f"Title: {current_title}\n"
        f"Budget: {budget}\n"
        f"Session: {session_status}\n"
        f"Run: {run_id}\n"
        f"Run Dir: {run_dir_path}\n"
        f"Last Screenshot: {last_shot}"
    )

    layout["header"].update(Panel(header, title="MR.N", style="bold cyan"))

    steps_table = Table(box=box.SIMPLE, expand=True)
    steps_table.add_column("#", width=4)
    steps_table.add_column("TYPE", width=12)
    steps_table.add_column("STATUS", width=10)
    steps_table.add_column("REASON")

    for record in actions[-15:]:
        steps_table.add_row(
            str(record.index),
            record.action.type,
            record.status,
            record.action.reason,
        )

    layout["steps"].update(Panel(steps_table, title="Actions"))

    log_table = Table(box=box.SIMPLE, expand=True)
    log_table.add_column("LEVEL", width=7)
    log_table.add_column("TAG", width=10)
    log_table.add_column("MESSAGE")
    logs = controller.get_logs()[-20:]
    for entry in logs:
        log_table.add_row(entry.level, entry.tag, entry.message)
    layout["logs"].update(Panel(log_table, title="Logs"))

    layout["input"].update(Panel("MR.N > Type /help for commands", title="Input"))

    return layout


def start_input_thread(cmd_queue: queue.Queue) -> threading.Thread:
    def loop() -> None:
        while True:
            try:
                command = console.input("MR.N > ").strip()
                cmd_queue.put(command)
            except (EOFError, KeyboardInterrupt):
                cmd_queue.put("exit")
                break

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread


def main() -> None:
    ensure_env()
    console.print(f"{APP_NAME} {APP_VERSION} ? Terminal Agent")
    console.print("Type /help for commands.\n")

    controller = AgentController(headless=False, trace=False, jsonl=False)
    cmd_queue: queue.Queue[str] = queue.Queue()
    start_input_thread(cmd_queue)

    running_thread: threading.Thread | None = None

    with Live(build_layout(controller), refresh_per_second=4, console=console, screen=False) as live:
        while True:
            live.update(build_layout(controller))
            try:
                command = cmd_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if command == "":
                continue
            if command == "exit":
                break
            if command == "/help":
                console.print(HELP_TEXT)
                continue

            if command.startswith("/new "):
                goal = command.replace("/new ", "", 1).strip()
                if running_thread and running_thread.is_alive():
                    console.print("Run already in progress.")
                    continue
                if not goal:
                    console.print("Provide a goal.")
                    continue
                running_thread = threading.Thread(target=controller.run_goal_sync, args=(goal,), daemon=True)
                running_thread.start()
                continue

            if command.startswith("/research "):
                goal = command.replace("/research ", "", 1).strip()
                console.print(asyncio.run(cmd_research(goal)))
                continue

            if command.startswith("/sources "):
                goal = command.replace("/sources ", "", 1).strip()
                console.print(asyncio.run(cmd_sources(goal)))
                continue

            if command == "/bench discovery":
                import asyncio as _asyncio
                from benchmarks.discovery_suite import run_suite
                _asyncio.run(run_suite())
                continue

            if command.startswith("/open-run "):
                run_id = command.replace("/open-run ", "", 1).strip()
                console.print(str(result_path(run_id)))
                continue

            if command == "/takeover":
                with controller.state.lock:
                    controller.state.mode = "TAKEOVER"
                console.print("TAKEOVER: Complete actions in browser then press ENTER")
                input()
                with controller.state.lock:
                    controller.state.mode = "SAFE"
                continue

            if command == "/stop":
                console.print("Stop requested")
                continue

            console.print("Unknown command. Type /help.")
            time.sleep(0.1)

if __name__ == "__main__":
    main()
