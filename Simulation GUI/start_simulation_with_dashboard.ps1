# PSA CodeSprint 2025 - Auto-Launch Script
# Launches simulation and dashboard simultaneously

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "  PSA CodeSprint 2025 - Port Simulation with Live Dashboard" -ForegroundColor Green
Write-Host "================================================================================`n" -ForegroundColor Cyan

# Launch dashboard in a new window
Write-Host "[1/2] Launching Streamlit Dashboard..." -ForegroundColor Yellow
$dashboardJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; streamlit run App/psa_dashboard.py" -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

# Launch simulation in this window
Write-Host "[2/2] Starting Simulation...`n" -ForegroundColor Yellow
Write-Host "Dashboard URL: http://localhost:8502" -ForegroundColor Cyan
Write-Host "Enable 'Auto-refresh (5s)' in the dashboard sidebar for live updates`n" -ForegroundColor Cyan

python cli.py

Write-Host "`n================================================================================`n" -ForegroundColor Cyan
Write-Host "Simulation completed!" -ForegroundColor Green
Write-Host "Dashboard is still running at: http://localhost:8502" -ForegroundColor Cyan
Write-Host "`nPress any key to close the dashboard..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop dashboard
if (!$dashboardJob.HasExited) {
    Stop-Process -Id $dashboardJob.Id -Force
    Write-Host "Dashboard closed.`n" -ForegroundColor Green
}
