# Spring Boot Local REST Service - PowerShell version
# For Windows 10/11 with PowerShell 5.1+

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "      Spring Boot Local REST Service          " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking environment..." -ForegroundColor Yellow

# Check Maven
try {
    $null = Get-Command mvn -ErrorAction Stop
    Write-Host "[OK] Maven found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Maven not found in PATH" -ForegroundColor Red
    Write-Host "Please install Maven and add it to system PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python
try {
    $null = Get-Command python -ErrorAction Stop
    Write-Host "[OK] Python found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python and add it to system PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Stopping existing services on port 8080 and 5001..." -ForegroundColor Yellow

# Stop processes on port 8080
$port8080 = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if ($port8080) {
    foreach ($conn in $port8080) {
        Write-Host "Stopping process $($conn.OwningProcess) on port 8080..." -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# Stop processes on port 5001
$port5001 = Get-NetTCPConnection -LocalPort 5001 -State Listen -ErrorAction SilentlyContinue
if ($port5001) {
    foreach ($conn in $port5001) {
        Write-Host "Stopping process $($conn.OwningProcess) on port 5001..." -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Waiting 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[1/2] Starting Python service (port 5001)..." -ForegroundColor Yellow

$pythonDir = Join-Path $PSScriptRoot "python"

$pythonJob = Start-Job -ScriptBlock {
    param($workDir)
    Set-Location $workDir
    python app.py
} -ArgumentList $pythonDir

Write-Host "Python service started as background job..." -ForegroundColor Green
Write-Host "Waiting 5 seconds for Python service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "[2/2] Starting Spring Boot service (port 8080)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " Services starting:" -ForegroundColor Cyan
Write-Host "  - Python: http://localhost:5001" -ForegroundColor Green
Write-Host "  - Spring Boot: http://localhost:8080" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop Spring Boot service" -ForegroundColor Yellow
Write-Host ""

try {
    Set-Location $PSScriptRoot
    mvn spring-boot:run
} finally {
    Write-Host ""
    Write-Host "[INFO] Stopping Python service..." -ForegroundColor Yellow
    Stop-Job $pythonJob -ErrorAction SilentlyContinue
    Remove-Job $pythonJob -Force -ErrorAction SilentlyContinue
    Write-Host "[INFO] All services stopped." -ForegroundColor Green
}

Write-Host ""
Read-Host "Press Enter to exit"
