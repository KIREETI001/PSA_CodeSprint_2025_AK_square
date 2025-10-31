# Quick Reference: Unified Analytics Engine

## 📦 Single Import
```python
from src.analytics.analytics_engine import AnalyticsEngine
from pathlib import Path

# Initialize once
analytics = AnalyticsEngine(Path("data/analytics_logs"))
```

## 🎯 All Methods Available

### Time Management
```python
analytics.update_simulation_time(current_time)
```

### Yard Job Counter
```python
analytics.record_job_completion(yard_name, job_type, job_seq, completion_time)
```

### HT Timeline Tracker
```python
analytics.create_timeline(job_seq, job_type, HT_name, QC_name, yard_name, instructions)
analytics.complete_job_timeline(job_seq, completion_time)
```

### Emissions Calculator
```python
analytics.calculate_emissions(job_seq, job_type, HT_name, instructions, timestamp)
```

### Route Optimizer
```python
analytics.analyze_route(job_seq, job_type, HT_name, route_type, path)
```

### Congestion Monitor
```python
analytics.update_congestion(ht_positions_dict, current_time)
```

### Summary & Export
```python
# Get overall summary from all modules
summary = analytics.get_overall_summary()
print(summary['yard_jobs'])      # Yard statistics
print(summary['timelines'])      # Timeline statistics
print(summary['emissions'])      # Emission statistics
print(summary['routes'])         # Route efficiency
print(summary['congestion'])     # Congestion status

# Export all summaries to CSV
analytics.export_all_summaries()
```

## 📊 Data Structure Access

### Direct Module Access (if needed)
```python
# Access individual modules through the analytics engine
analytics.yard_counter.get_total_jobs()
analytics.timeline_tracker.get_summary_stats()
analytics.emissions_calculator.get_summary()
analytics.route_optimizer.get_efficiency_summary()
analytics.congestion_monitor.get_current_status()
```

## 📁 CSV Outputs
All generated in `data/analytics_logs/`:
- `yard_job_counts.csv` - Yard job completions
- `ht_timelines.csv` - HT job timelines
- `emissions.csv` - Detailed emissions per segment
- `emissions_summary.csv` - Emission totals
- `route_optimization.csv` - Route analysis
- `route_summary.csv` - Route efficiency summary
- `congestion_events.csv` - Congestion event log
- `congestion_alerts.csv` - Congestion alerts

## 🔥 Example: Complete Job Flow

```python
from src.analytics.analytics_engine import AnalyticsEngine
from pathlib import Path

# 1. Initialize
analytics = AnalyticsEngine(Path("data/analytics_logs"))

# 2. Update time
analytics.update_simulation_time(100.0)

# 3. Create timeline when job is planned
analytics.create_timeline(
    job_seq="J001",
    job_type="DI",
    HT_name="HT_1",
    QC_name="QC_1",
    yard_name="A1",
    instructions=job_instructions
)

# 4. Calculate emissions
analytics.calculate_emissions(
    job_seq="J001",
    job_type="DI",
    HT_name="HT_1",
    instructions=job_instructions,
    timestamp=100.0
)

# 5. Analyze routes
for instruction in job_instructions:
    if hasattr(instruction, 'path'):
        analytics.analyze_route(
            job_seq="J001",
            job_type="DI",
            HT_name="HT_1",
            route_type="BUFFER_TO_QC",
            path=instruction.path
        )

# 6. Update congestion
ht_positions = {"HT_1": Coordinate(10, 5), "HT_2": Coordinate(11, 5)}
analytics.update_congestion(ht_positions, 100.0)

# 7. Record completion
analytics.record_job_completion(
    yard_name="A1",
    job_type="DI",
    job_seq="J001",
    completion_time=150.0
)

# 8. Complete timeline
analytics.complete_job_timeline("J001", 150.0)

# 9. Get summary
summary = analytics.get_overall_summary()
print(f"Total jobs: {summary['yard_jobs']['total_jobs']}")
print(f"Total emissions: {summary['emissions']['total_emissions_kg']} kg")
print(f"Route efficiency: {summary['routes']['avg_efficiency']}%")

# 10. Export all data
analytics.export_all_summaries()
```

## ✨ Key Benefits

1. **One Import** - Import once, get everything
2. **Unified Interface** - All methods through single object
3. **Easy Deployment** - Copy one file: `analytics_engine.py`
4. **Zero Breaking Changes** - All original functionality preserved
5. **Cleaner Code** - No multiple module management

---
**That's it!** All analytics in one place. 🎉
