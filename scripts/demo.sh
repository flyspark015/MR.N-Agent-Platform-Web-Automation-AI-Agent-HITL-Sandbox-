#!/usr/bin/env bash
set -e

echo "Demo 1: Open https://example.com and tell me the title"
echo "Demo 2: Search Google for OpenAI official site and open it"
echo "Demo 3: Search Google for <query> and extract top 3 results"
echo "Run the CLI and enter /new <goal> with the demo goals above."
python -m apps.cli.main
