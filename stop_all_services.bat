@echo off
echo =================================================================
echo    Stopping All Snitch Luxe Microservices...
echo =================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0stop_all_services.ps1"
pause
