# 🚀 Live Dashboard Setup Guide

## ✅ Integration Status: COMPLETE

All three components are properly integrated:
- ✅ **job_planner.py** → Tracks all telemetry (emissions, ETA, yard capacity, congestion, HT utilization, route efficiency)
- ✅ **logging_manager.py** → Writes data to 6 CSV files in real-time
- ✅ **psa_dashboard.py** → Reads CSV files and auto-refreshes every 5 seconds

## 🎯 How to View Live Data

### Option 1: Two Terminals (Recommended for Live Updates)

**Terminal 1 - Run Simulation:**
```powershell
cd "Simulation GUI"
python cli.py
```

**Terminal 2 - Run Dashboard (in a separate terminal):**
```powershell
cd "Simulation GUI"
streamlit run App/psa_dashboard.py
```

**Dashboard Settings:**
- ✅ Enable "🔄 Auto-refresh (5s)" checkbox in sidebar (enabled by default)
- Watch the data update every 5 seconds as the simulation progresses!

### Option 2: Run Simulation First, Then View Results

**Step 1 - Generate Data:**
```powershell
cd "Simulation GUI"
python cli.py
```

**Step 2 - View Dashboard:**
```powershell
streamlit run App/psa_dashboard.py
```
- Dashboard will show all completed data
- Auto-refresh can be disabled since simulation is done

## 📊 What You'll See

### Real-Time Metrics (Updates every 5 seconds):
1. **📈 Total Jobs Processed** - Live count as jobs complete
2. **🌱 Total CO2 Emissions** - Accumulating emissions in real-time
3. **⏱️ Average ETA** - Real-time ETA calculations
4. **📦 Active Yards** - Yard count updates as simulation runs

### 6 Live Visualizations:
1. **🌍 Emissions Pie Chart** - DI vs Load job emissions breakdown
2. **📊 Yard Capacity Charts** - All 16 yards with Total/DI/Load capacity bars
3. **📈 ETA Analysis** - Histogram and yard-wise ETA distribution
4. **🔥 Congestion Heatmap** - Shows bottlenecks (if any occur)
5. **🚛 HT Fleet Utilization** - 80 HTs with active/idle time breakdown
6. **🛣️ Route Efficiency** - Performance metrics for all routes

## 🔧 Troubleshooting

### Dashboard shows "Waiting for data..."
- ✅ **Solution**: Run `python cli.py` first to generate CSV files
- Check that CSV files exist in `App/data/` folder

### Dashboard not updating live
- ✅ **Solution 1**: Enable "🔄 Auto-refresh (5s)" checkbox in sidebar
- ✅ **Solution 2**: Run simulation and dashboard in separate terminals simultaneously

### CSV files are empty
- ✅ **Fixed**: All logging functions now working correctly
- emission_log.csv should have 20,000+ rows after full simulation
- All 6 CSV files generate data properly

## 📁 CSV Files Generated

| File | Rows (Full Simulation) | Description |
|------|------------------------|-------------|
| `emission_log.csv` | 20,001 | CO2 emissions per job with distance/HT/yard details |
| `eta_tracker.csv` | 20,001 | Estimated arrival times for all jobs |
| `yard_capacity_log.csv` | 20,001 | Real-time capacity tracking for 16 yards |
| `ht_utilization_log.csv` | ~2,000 | HT fleet status (logged every 10 jobs per HT) |
| `route_efficiency_log.csv` | ~2,000 | Route performance (10% sampling) |
| `congestion_log.csv` | 3-50 | Congestion events (only when detected) |

## 🎉 Success Criteria

✅ All CSV files have data (check row counts > 1)
✅ Dashboard loads without errors
✅ Real job IDs appear (e.g., JOB6022768C, not "UNKNOWN")
✅ Emission values are realistic (0.2 - 1.5 kg CO2)
✅ Yard capacity shows accurate DI/LO breakdown
✅ Auto-refresh updates every 5 seconds (when enabled)

## 🚀 Performance Notes

- **Simulation Runtime**: ~30-40 seconds for 20,000 jobs
- **Dashboard Refresh**: 5 seconds (configurable)
- **CSV File Size**: ~2-3 MB total for all 6 files
- **Memory Usage**: Minimal - uses file-based logging, no in-memory accumulation

## 📝 Next Steps

1. ✅ **Integration Testing**: Complete - all systems working
2. ✅ **Data Validation**: Complete - real job IDs, accurate metrics
3. 🎯 **Live Dashboard**: Follow Option 1 above for real-time updates
4. 📊 **Analysis**: Use dashboard visualizations for insights

---

**Last Updated**: October 19, 2025
**Integration Status**: ✅ FULLY OPERATIONAL
