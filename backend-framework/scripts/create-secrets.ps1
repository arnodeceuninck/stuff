# Generic secret-file generator for local Docker development.
# Reads every KEY=VALUE pair from .env in the CURRENT directory and writes
# each value to secrets/<lowercase-key> so Docker Compose / Swarm can mount
# them as file-based secrets.
#
# Usage (run from each service repo root):
#
#   cd auth-service
#   ..\..\backend-framework\scripts\create-secrets.ps1
#
#   cd ..\stuff
#   ..\backend-framework\scripts\create-secrets.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Write-Error ".env not found in $PWD.  Copy .env.example to .env and fill in values."
    exit 1
}

$values = @{}
Get-Content ".env" | Where-Object { $_ -match "^[A-Za-z_][A-Za-z0-9_]*=" } | ForEach-Object {
    $parts = $_ -split "=", 2
    $values[$parts[0].Trim()] = $parts[1].Trim()
}

New-Item -Path "secrets" -ItemType Directory -Force | Out-Null

foreach ($key in $values.Keys) {
    $filename = $key.ToLower()
    [System.IO.File]::WriteAllText("$PWD\secrets\$filename", $values[$key])
    Write-Host "  created secrets/$filename"
}

Write-Host "Done. Secret files written to secrets/ (gitignored)."
