from __future__ import annotations

import os
from pathlib import Path
from getpass import getpass

ENV_PATH = Path(".env")
EXAMPLE_PATH = Path(".env.example")


def ensure_env() -> None:
    if os.getenv("OPENAI_API_KEY"):
        return
    if ENV_PATH.exists():
        return
    if EXAMPLE_PATH.exists():
        ENV_PATH.write_text(EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        ENV_PATH.write_text("OPENAI_API_KEY=\n", encoding="utf-8")

    print("[SETUP] .env created. Please enter your OpenAI API key.")
    key = getpass("OPENAI_API_KEY (input hidden): ")
    if key and key.startswith("sk-"):
        content = ENV_PATH.read_text(encoding="utf-8")
        content = "\n".join(
            [
                f"OPENAI_API_KEY={key}" if line.startswith("OPENAI_API_KEY=") else line
                for line in content.splitlines()
            ]
        )
        ENV_PATH.write_text(content + "\n", encoding="utf-8")
        print("[SETUP] API key saved to .env")
    else:
        print("[SETUP] Invalid key format. Set OPENAI_API_KEY in .env manually.")
