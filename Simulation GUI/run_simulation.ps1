# PSA CodeSprint 2025 - Auto-Launch Script
# This script runs the simulation and dashboard automatically

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "🚀 PSA CodeSprint 2025 - Port Simulation Engine" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "📊 Starting simulation with live dashboard..." -ForegroundColor Yellow
Write-Host "   Simulation: Running in this terminal" -ForegroundColor Gray
Write-Host "   Dashboard: Will open at http://localhost:8502`n" -ForegroundColor Gray

# Run the simulation (dashboard launches automatically from job_planner)
python cli.py

Write-Host "`n✅ Simulation completed!" -ForegroundColor Green
Write-Host "📊 Dashboard may still be running at http://localhost:8502" -ForegroundColor Cyan
Write-Host "   Close the dashboard window when done.`n" -ForegroundColor Gray
