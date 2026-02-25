param(
  [string]$Query = "OpenAI official site"
)

Write-Host "Demo 1: Open https://example.com and tell me the title"
Write-Host "Demo 2: Search Google for OpenAI official site and open it"
Write-Host "Demo 3: Search Google for $Query and extract top 3 results"
Write-Host "Run the CLI and enter /new <goal> with the demo goals above."
python -m apps.cli.main
