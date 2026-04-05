param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$authRepo = Join-Path $repoRoot "auth-service"
$stuffRepo = Join-Path $repoRoot "stuff"

if (-not (Test-Path $authRepo) -or -not (Test-Path $stuffRepo)) {
    Write-Error "Expected auth-service/ and stuff/ directories under $repoRoot"
    exit 1
}

Write-Host "==> Generating secret files from .env"
Push-Location $authRepo
& (Join-Path $scriptDir "create-secrets.ps1")
Pop-Location

Push-Location $stuffRepo
& (Join-Path $scriptDir "create-secrets.ps1")
Pop-Location

if (-not $SkipBuild) {
    Write-Host "==> Building shared base image"
    Push-Location (Join-Path $repoRoot "backend-framework")
    docker compose -f compose.build.yml build
    Pop-Location

    Write-Host "==> Building service images"
    Push-Location $authRepo
    docker compose -f compose.build.yml build
    Pop-Location

    Push-Location $stuffRepo
    docker compose -f compose.build.yml build
    Pop-Location
}

Write-Host "==> Starting auth-service stack"
Push-Location $authRepo
# run detached so both stacks can be started in one script

docker compose up -d
Pop-Location

Write-Host "==> Starting stuff stack"
Push-Location $stuffRepo
docker compose up -d
Pop-Location

Write-Host "All services started."
Write-Host "Auth API:  http://localhost:8001/docs"
Write-Host "Stuff API: http://localhost:8000/docs"
