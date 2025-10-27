# scripts/fix-ruff-config.ps1
# Gebruik:  powershell -ExecutionPolicy Bypass -File scripts\fix-ruff-config.ps1
# Vereist: actieve venv (.\.venv\Scripts\Activate.ps1) of python in PATH.

$ErrorActionPreference = 'Stop'

function Write-Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# 1) Pad controleren
$RepoRoot = Split-Path -Parent $PSCommandPath
while (!(Test-Path (Join-Path $RepoRoot ".git"))) {
  $parent = Split-Path -Parent $RepoRoot
  if ([string]::IsNullOrEmpty($parent) -or $parent -eq $RepoRoot) {
    Write-Err "Kon de repo-root (.git) niet vinden. Start dit script vanuit de repo."
    exit 2
  }
  $RepoRoot = $parent
}
Set-Location $RepoRoot
Write-Info "Repo-root: $RepoRoot"

# 2) Gewenste inhoud voor .ruff.toml (UTF-8 zonder BOM)
$ruffTomlDesired = @"
# .ruff.toml
# Dit bestand MOET UTF-8 zonder BOM zijn. Geen lege regel boven deze comment.

[tool.ruff]
select = ["E", "F", "I"]
fix = true
fixable = ["ALL"]
line-length = 100
respect-gitignore = true

[tool.ruff.per-file-ignores]
"agent/tasks/*.py" = ["E401"]
"@

$ruffPath = Join-Path $RepoRoot ".ruff.toml"

# 3) Huidig bestand inlezen (bytes) en check op BOM
$hasExisting = Test-Path $ruffPath
if ($hasExisting) {
  $bytes = [System.IO.File]::ReadAllBytes($ruffPath)
  if ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) {
    Write-Warn ".ruff.toml bevat een UTF-8 BOM (EF BB BF). Deze wordt verwijderd."
    $bytesNoBom = $bytes[3..($bytes.Length-1)]
    [System.IO.File]::WriteAllBytes($ruffPath, $bytesNoBom)
    Write-Ok "BOM verwijderd."
  }
} else {
  Write-Warn ".ruff.toml bestond nog niet; het bestand wordt aangemaakt."
}

# 4) Overschrijf met de gewenste, correcte inhoud (ZONDER BOM)
#    Gebruik .NET om gegarandeerd UTF-8 zonder BOM te schrijven (compatibel met Windows PowerShell 5.x)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)  # false => no BOM
[System.IO.File]::WriteAllText($ruffPath, $ruffTomlDesired, $utf8NoBom)
Write-Ok ".ruff.toml overschreven met correcte inhoud (UTF-8 no BOM)."

# 5) Verifieer dat er geen BOM meer is
$head3 = (Get-Content $ruffPath -Encoding Byte -TotalCount 3)
if ($head3.Count -ge 3) {
  $hex = ('{0:X2}{1:X2}{2:X2}' -f $head3[0],$head3[1],$head3[2])
  if ($hex -eq 'EFBBBF') {
    Write-Err "BOM staat nog in .ruff.toml. Stop."
    exit 3
  }
}
Write-Ok "Geen BOM gedetecteerd in .ruff.toml."

# 6) Ruff installeren in de actieve Python-omgeving
Write-Info "Installeer/upgrade ruff…"
python -c "import sys; print(sys.version)" | Out-Null
python -m pip install --upgrade pip ruff | Out-Null
$ruffVersion = & python -m ruff --version
Write-Ok "Ruff geïnstalleerd: $ruffVersion"

# 7) Ruff check draaien (met .ruff.toml)
Write-Info "Ruff check ."
# Gebruik het modulepad om zeker te zijn dat we de ruff uit de venv gebruiken
python -m ruff check . --output-format=github
Write-Ok "Ruff check geslaagd."

Write-Info "Klaar. Commit en push nu je gewijzigde .ruff.toml."
