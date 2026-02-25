from __future__ import annotations

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
from storage.fs import result_path

console = Console()

HELP_TEXT = """Commands:
  /new <goal>
  /retry
  /pause
  /resume
  /cancel
  /export
  /open-last-screenshot
  /help
  exit
"""

def build_layout(controller: AgentController) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="status", size=3),
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

    status_text = f"{status} | {current_url}" if current_url else status
    if current_title:
        status_text = f"{status_text} | {current_title}"
    layout["status"].update(Panel(status_text, title="Status", style="bold cyan"))

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
    log_table.add_column("TAG", width=10)
    log_table.add_column("MESSAGE")
    logs = controller.get_logs()[-20:]
    for entry in logs:
        log_table.add_row(f"[{entry.tag}]", entry.message)
    layout["logs"].update(Panel(log_table, title="Logs"))

    layout["input"].update(Panel("Type /help for commands", title="Input"))

    return layout


def start_input_thread(cmd_queue: queue.Queue) -> threading.Thread:
    def loop() -> None:
        while True:
            try:
                command = console.input("? ").strip()
                cmd_queue.put(command)
            except (EOFError, KeyboardInterrupt):
                cmd_queue.put("exit")
                break

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread


def main() -> None:
    console.print("MR.N CLI Agent (TUI)")
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

            if command == "/retry":
                goal = controller.state.last_goal
                if not goal:
                    console.print("No previous goal.")
                    continue
                if running_thread and running_thread.is_alive():
                    console.print("Run already in progress.")
                    continue
                running_thread = threading.Thread(target=controller.run_goal_sync, args=(goal,), daemon=True)
                running_thread.start()
                continue

            if command == "/pause":
                controller.pause()
                console.print("Paused.")
                continue

            if command == "/resume":
                controller.resume()
                console.print("Resumed.")
                continue

            if command == "/cancel":
                controller.cancel()
                console.print("Cancel requested.")
                continue

            if command == "/export":
                if controller.state.task_id:
                    console.print(str(result_path(controller.state.task_id)))
                else:
                    console.print("No run yet.")
                continue

            if command == "/open-last-screenshot":
                with controller.state.lock:
                    shot = controller.state.last_screenshot
                if not shot:
                    console.print("No run yet.")
                    continue
                console.print(shot)
                continue

            console.print("Unknown command. Type /help.")

            time.sleep(0.1)

if __name__ == "__main__":
    main()
