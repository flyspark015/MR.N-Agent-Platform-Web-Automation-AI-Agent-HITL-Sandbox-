param(
  [string]$BinDir = "$env:USERPROFILE\bin"
)

$ErrorActionPreference = "Stop"

try {
  if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
  }

  if (-not (Test-Path ".venv")) {
    python -m venv .venv
  }

  . .\.venv\Scripts\activate
  pip install -r requirements.txt
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Install failed"
    exit 1
  }

  python -m playwright install chromium
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Install failed"
    exit 1
  }

  $shim = @'
param()
Set-Location "{REPO_DIR}"
. .\.venv\Scripts\activate
python -m apps.cli.main
'@

  $repoDir = (Resolve-Path ".").Path
  $shim = $shim.Replace("{REPO_DIR}", $repoDir)
  $shimPath = Join-Path $BinDir "mrn.ps1"
  $shim | Set-Content -Encoding ASCII -Path $shimPath

  $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
  if (-not $userPath) { $userPath = "" }
  if ($userPath -notlike "*$BinDir*") {
    $newPath = $userPath.TrimEnd(";")
    if ($newPath) { $newPath += ";" }
    $newPath += $BinDir
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "Added $BinDir to PATH (User). Restart PowerShell to use 'mrn'."
  }

  Write-Host "Install complete. Open a new PowerShell window and run: mrn"
}
catch {
  Write-Host "Install failed"
  Write-Host $_
  exit 1
}
