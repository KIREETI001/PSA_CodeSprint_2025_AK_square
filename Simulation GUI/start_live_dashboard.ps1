# PSA Port Operations - Live Dashboard Launcher
# This script starts both the simulation and dashboard in separate windows

Write-Host "`n🚀 PSA LIVE DASHBOARD LAUNCHER" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "This will open 2 windows:" -ForegroundColor Yellow
Write-Host "  1. Simulation Engine (generating live data)" -ForegroundColor Green
Write-Host "  2. Dashboard (visualizing data in real-time)`n" -ForegroundColor Green

Write-Host "Press any key to start..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n📊 Starting Simulation Engine..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; Write-Host '`n🔧 SIMULATION ENGINE RUNNING' -ForegroundColor Green; Write-Host 'Generating telemetry data...`n' -ForegroundColor Gray; python cli.py"

Write-Host "⏳ Waiting 3 seconds for CSV files to initialize...`n" -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "🌐 Starting Dashboard..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; Write-Host '`n📊 DASHBOARD RUNNING' -ForegroundColor Green; Write-Host 'Access at: http://localhost:8502`n' -ForegroundColor Cyan; streamlit run App/psa_dashboard.py"

Write-Host "`n✅ Both systems launched!" -ForegroundColor Green
Write-Host "`nDashboard URL: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:8502" -ForegroundColor Cyan
Write-Host "`nTIP: Enable 'Auto-refresh (5s)' in the dashboard sidebar`n" -ForegroundColor Yellow

Write-Host "Press any key to exit this launcher (systems will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
