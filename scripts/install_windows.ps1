param(
  [string]$InstallDir = "$env:USERPROFILE\bin"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $InstallDir)) {
  New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
}

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

. .\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

$shim = Join-Path $InstallDir "mrn.ps1"
$shimContent | Set-Content -Encoding ASCII $shim

$path = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($path -notlike "*${InstallDir}*") {
  [Environment]::SetEnvironmentVariable("PATH", "$path;$InstallDir", "User")
  Write-Host "Added $InstallDir to PATH (User). Restart PowerShell to use 'mrn'."
}

Write-Host "Install complete. Open a new PowerShell window and run: mrn"
