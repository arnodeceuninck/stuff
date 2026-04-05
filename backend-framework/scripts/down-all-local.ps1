$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$authRepo = Join-Path $repoRoot "auth-service"
$stuffRepo = Join-Path $repoRoot "stuff"

if (Test-Path $authRepo) {
    Write-Host "==> Stopping auth-service stack"
    Push-Location $authRepo
    docker compose down
    Pop-Location
}

if (Test-Path $stuffRepo) {
    Write-Host "==> Stopping stuff stack"
    Push-Location $stuffRepo
    docker compose down
    Pop-Location
}

Write-Host "All local stacks stopped."
