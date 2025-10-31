# 🔄 Logging Manager Migration Guide

## Overview

We've refactored all logging operations into a centralized `LoggingManager` class for better code organization and maintainability.

## New Architecture

### Before:
```
job_planner.py (1000+ lines)
├── Planning logic
├── Emission logging
├── ETA logging
├── Yard capacity logging
├── Congestion logging
└── All CSV file management
```

### After:
```
job_planner.py (cleaner, focused)
├── Planning logic only
└── Uses LoggingManager for all logging

logging_manager.py (separate module)
├── All CSV file initialization
├── Emission logging
├── ETA logging
├── Yard capacity logging
├── Congestion logging
├── HT utilization logging (NEW)
├── QC performance logging (NEW)
├── Route efficiency logging (NEW)
├── Strategy performance logging (NEW)
└── Dwell time logging (NEW)
```

## How to Use in job_planner.py

### Step 1: Import the LoggingManager

```python
from src.utils.logging_manager import get_logging_manager
```

### Step 2: Initialize in __init__

```python
class JobPlanner:
    def __init__(self):
        # ... existing code ...
        
        # Initialize centralized logging manager
        self.logger = get_logging_manager()
```

### Step 3: Replace Old Logging Calls

**OLD WAY (scattered throughout code):**
```python
# Emission logging (old)
with open(self._emission_log_path, "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        job_id, job_type, qc, yard, ht_name, distance, emission
    ])

# ETA logging (old)
with open(self._eta_log_path, "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow([...])
```

**NEW WAY (clean single line):**
```python
# Emission logging (new)
self.logger.log_emission(job_id, job_type, qc, yard, ht_name, distance, emission)

# ETA logging (new)
self.logger.log_eta(job_id, ht_name, qc, yard, distance, eta_seconds)
```

## Complete Logging API

### 1. Emission Logging
```python
self.logger.log_emission(
    job_id="JOB_001",
    job_type="DI",
    qc="QC1",
    yard="A1",
    ht_name="HT_01",
    distance=25,
    emission=0.755  # kg CO2
)
```

### 2. ETA Logging
```python
self.logger.log_eta(
    job_id="JOB_001",
    ht_name="HT_01",
    qc="QC1",
    yard="A1",
    distance=25,
    eta_seconds=120
)
```

### 3. Yard Capacity Logging
```python
self.logger.log_yard_capacity(
    yard_name="A1",
    total_jobs=150,
    discharge_jobs=100,
    load_jobs=50,
    alert="WARNING: Near capacity"
)
```

### 4. Congestion Logging
```python
self.logger.log_congestion(
    congestion_type="HT_SHORTAGE",
    location="GLOBAL",
    severity="HIGH",
    available_hts=3,
    pending_jobs=50,
    strategy="aggressive",
    description="Very few HTs available for large job queue"
)
```

### 5. HT Utilization Logging (NEW)
```python
self.logger.log_ht_utilization(
    ht_name="HT_01",
    status="ACTIVE",
    current_job_id="JOB_001",
    jobs_completed=25,
    total_distance=500,
    active_time=3600,  # seconds
    idle_time=300      # seconds
)
```

### 6. QC Performance Logging (NEW)
```python
self.logger.log_qc_performance(
    qc_name="QC1",
    containers_processed=150,
    cycle_time_avg=45.5,  # seconds per container
    idle_time=600,         # seconds
    discharge_count=100,
    load_count=50
)
```

### 7. Route Efficiency Logging (NEW)
```python
self.logger.log_route_efficiency(
    ht_name="HT_01",
    origin="QC1",
    destination="A1",
    job_type="DI",
    distance=25,
    actual_time=125,    # seconds
    optimal_time=120,   # seconds
    congestion=False
)
```

### 8. Strategy Performance Logging (NEW)
```python
self.logger.log_strategy_performance(
    strategy="aggressive",
    jobs_planned=100,
    avg_job_time=115.5,
    congestion_events=2,
    ht_utilization=85.5,
    total_emissions=150.75
)
```

### 9. Dwell Time Logging (NEW)
```python
from datetime import datetime

self.logger.log_dwell_time(
    container_id="CONT_12345",
    yard_name="A1",
    job_type="DI",
    arrival_time=datetime(2025, 10, 19, 10, 0),
    departure_time=datetime(2025, 10, 22, 14, 30),
    target_dwell_hours=72.0
)
```

### 10. Batch Logging (Convenience Method)
```python
job_data = {
    'job_id': 'JOB_001',
    'job_type': 'DI',
    'qc': 'QC1',
    'yard': 'A1',
    'ht_name': 'HT_01',
    'distance': 25,
    'emission': 0.755,
    'eta': 120,
    'actual_time': 125,
    'optimal_time': 120,
    'origin': 'QC1',
    'destination': 'A1',
    'congestion': False
}

# Logs emission, ETA, and route efficiency in one call
self.logger.log_job_complete(job_data)
```

## Migration Steps

### 1. Remove Old Logging Code from job_planner.py

**Delete these sections:**
- CSV file path definitions in `__init__`
- CSV file initialization code
- All `with open(...) as f:` logging blocks
- Individual logging helper methods

### 2. Add LoggingManager Import

```python
from src.utils.logging_manager import get_logging_manager
```

### 3. Initialize in Constructor

```python
def __init__(self):
    # ... existing initialization ...
    self.logger = get_logging_manager()
```

### 4. Replace Logging Calls

Find and replace all logging code:
- `self._log_emission(...)` → `self.logger.log_emission(...)`
- `self._log_eta(...)` → `self.logger.log_eta(...)`
- `self._log_yard_capacity(...)` → `self.logger.log_yard_capacity(...)`
- `self._log_congestion(...)` → `self.logger.log_congestion(...)`

### 5. Add New Logging Calls

Add calls to new loggers where appropriate:
- Track HT utilization at key points
- Log QC performance after processing containers
- Record route efficiency for each job
- Track strategy performance when switching strategies
- Monitor dwell time when containers enter/leave yards

## Benefits

✅ **Cleaner Code**: job_planner.py focuses only on planning logic  
✅ **Better Maintainability**: All logging in one place  
✅ **Easier Testing**: Can test logging independently  
✅ **More Readable**: Clear separation of concerns  
✅ **Scalable**: Easy to add new loggers  
✅ **Consistent**: All logs use same patterns  
✅ **Error Handling**: Built-in try-except in all log methods  
✅ **Performance**: No impact on main planning logic  

## Dashboard Integration

All new log files are automatically supported by the dashboard:
- `ht_utilization_log.csv` - HT performance metrics
- `qc_performance_log.csv` - Crane efficiency
- `route_efficiency_log.csv` - Travel optimization
- `strategy_performance_log.csv` - Planning effectiveness
- `dwell_time_log.csv` - Container storage duration

You can add visualization sections to `psa_dashboard.py` to display these new metrics!

## Next Steps

1. ✅ LoggingManager created
2. ⏳ Update job_planner.py to use LoggingManager
3. ⏳ Add logging calls for new metrics
4. ⏳ Update dashboard with new visualizations
5. ⏳ Test all logging operations

Would you like me to proceed with updating job_planner.py?
