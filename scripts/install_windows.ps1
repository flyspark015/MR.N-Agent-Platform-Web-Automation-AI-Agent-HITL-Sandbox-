param(
  [string] = "C:\Users\toy4y\bin"
)

Continue = "Stop"

try {
  if (-not (Test-Path )) {
    New-Item -ItemType Directory -Force -Path  | Out-Null
  }

  if (-not (Test-Path ".venv")) {
    python -m venv .venv
  }

  . .\.venv\Scripts\activate
  pip install -r requirements.txt
  python -m playwright install chromium

   = @'
param()
Set-Location "\..\mrn"
. .\.venv\Scripts\activate
python -m apps.cli.main
'@

   = Join-Path  "mrn.ps1"
   | Set-Content -Encoding ASCII 

   = [Environment]::GetEnvironmentVariable("PATH", "User")
  if ( -notlike "**") {
    [Environment]::SetEnvironmentVariable("PATH", ";", "User")
    Write-Host "Added  to PATH (User). Restart PowerShell to use 'mrn'."
  }

  Write-Host "Install complete. Open a new PowerShell window and run: mrn"
}
catch {
  Write-Host "Install failed"
  Write-Host 
  exit 1
}
