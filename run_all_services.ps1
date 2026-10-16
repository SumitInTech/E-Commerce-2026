# ==============================================================================
# SNITCH LUXE AI E-COMMERCE - MASTER MICROSERVICES LAUNCHER (PowerShell)
# ==============================================================================
# Runs all 8 microservices concurrently in the background.
# Usage:
#   .\run_all_services.ps1
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "   Starting All 8 Snitch Luxe Microservices in Background...    " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$services = @(
    @{ Name = "API Gateway";      Module = "backend.api_gateway.main:app";      Port = 8000 },
    @{ Name = "Auth Service";     Module = "backend.auth.main:app";             Port = 8001 },
    @{ Name = "Payment Service";  Module = "backend.payment.main:app";          Port = 8002 },
    @{ Name = "Catalog Service";  Module = "backend.catalog.main:app";          Port = 8003 },
    @{ Name = "Order Service";    Module = "backend.order.main:app";            Port = 8004 },
    @{ Name = "Admin Service";    Module = "backend.customer_admin.main:app";   Port = 8005 },
    @{ Name = "AI Fit Service";   Module = "backend.ai_fit.main:app";           Port = 8006 },
    @{ Name = "AI Chatbot";       Module = "backend.chatbot.main:app";          Port = 8007 }
)

$pids_list = @()
$root_dir = $PSScriptRoot
if (-not $root_dir) { $root_dir = Get-Location }

foreach ($svc in $services) {
    Write-Host "[Starting] $($svc.Name) on port $($svc.Port)..." -ForegroundColor Yellow
    
    # Launch uvicorn via python in background window
    $proc = Start-Process -FilePath "python" `
        -ArgumentList "-m uvicorn $($svc.Module) --host 127.0.0.1 --port $($svc.Port)" `
        -WorkingDirectory $root_dir `
        -PassThru `
        -WindowStyle Minimized

    $pids_list += [PSCustomObject]@{
        Name = $svc.Name
        Port = $svc.Port
        PID  = $proc.Id
        URL  = "http://127.0.0.1:$($svc.Port)"
        Docs = "http://127.0.0.1:$($svc.Port)/docs"
    }
}

# Save PIDs to file for stop script
$pids_list | ConvertTo-Json | Set-Content -Path (Join-Path $root_dir ".services_pids.json") -Force

Write-Host "`nWaiting 3 seconds for microservices to initialize..." -ForegroundColor DarkGray
Start-Sleep -Seconds 3

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "             ALL 8 MICROSERVICES ARE RUNNING!                   " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

$pids_list | Format-Table -Property Name, Port, PID, URL, Docs

Write-Host "To STOP all running microservices anytime, run:" -ForegroundColor Yellow
Write-Host "   .\stop_all_services.ps1`n" -ForegroundColor White
