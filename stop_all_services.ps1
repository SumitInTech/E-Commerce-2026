# ==============================================================================
# SNITCH LUXE AI E-COMMERCE - STOP MICROSERVICES SCRIPT (PowerShell)
# ==============================================================================
# Gracefully stops all background microservices.
# Usage:
#   .\stop_all_services.ps1
# ==============================================================================

Write-Host "Stopping all Snitch Luxe microservices..." -ForegroundColor Yellow

$root_dir = $PSScriptRoot
if (-not $root_dir) { $root_dir = Get-Location }
$pid_file = Join-Path $root_dir ".services_pids.json"

if (Test-Path $pid_file) {
    $svcs = Get-Content -Path $pid_file | ConvertFrom-Json
    foreach ($svc in $svcs) {
        try {
            Stop-Process -Id $svc.PID -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped $($svc.Name) (PID: $($svc.PID), Port: $($svc.Port))" -ForegroundColor Green
        } catch {
            Write-Host "Process for $($svc.Name) was already stopped." -ForegroundColor DarkGray
        }
    }
    Remove-Item -Path $pid_file -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "PID file not found. Scanning and terminating processes on ports 8000-8007..." -ForegroundColor Yellow
}

# Fallback port cleanup for 8000 through 8007
8000..8007 | ForEach-Object {
    $port = $_
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $conns | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {
            try {
                Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
                Write-Host "Killed residual process $_ on port $port" -ForegroundColor Green
            } catch {}
        }
    }
}

Write-Host "All microservices have been successfully stopped." -ForegroundColor Cyan
