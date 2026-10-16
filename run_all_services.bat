@echo off
echo =================================================================
echo    Starting All 8 Snitch Luxe Microservices in Background...
echo =================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0run_all_services.ps1"
pause
