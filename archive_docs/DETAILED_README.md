# PSA CodeSprint 2025: Smart Port Operations - Complete Setup Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Running the Simulation](#running-the-simulation)
5. [Analytics Dashboard](#analytics-dashboard)
6. [Project Structure](#project-structure)
7. [Understanding the Analytics](#understanding-the-analytics)
8. [Troubleshooting](#troubleshooting)
9. [Submission Guidelines](#submission-guidelines)

---

## Overview

This project implements an AI-driven scheduling and routing strategy for horizontal transport optimization in a port terminal. The system includes:
- **Planning Engine**: Smart scheduling and routing algorithms
- **Operation Engine**: Realistic simulation of port operations
- **Analytics Dashboard**: Real-time monitoring with 5 analytics modules
- **CLI & GUI**: Both command-line and graphical interfaces

### Key Features
- ✅ Real-time analytics tracking
- ✅ Emissions monitoring (DI vs LO jobs)
- ✅ Route optimization analysis
- ✅ Yard job counters with visual charts
- ✅ HT timeline tracking
- ✅ Congestion detection

---

## 🔧 Prerequisites

Before starting, ensure you have:
- **Python 3.10 or 3.11** installed (3.11 recommended)
- **pip** package manager
- **Windows PowerShell** or Command Prompt
- At least **2GB free disk space**
- **Internet connection** for downloading dependencies

### Verify Python Installation
```powershell
python --version
# Should output: Python 3.11.x or Python 3.10.x
```

---

## Initial Setup

### Step 1: Navigate to Project Directory
### Step 2: Create Virtual Environment
```powershell
# Install virtualenv if not already installed
python -m pip install virtualenv

# Create virtual environment
python -m virtualenv venv

# Activate the environment
.\venv\Scripts\Activate.ps1
```

**Note**: If you encounter execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```powershell
# Install pip-tools for dependency management
python -m pip install pip-tools

# Compile and install dependencies
pip-compile -v --rebuild -o requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
pip-sync requirements.txt
```

### Step 4: Create Dashboard Virtual Environment
The analytics dashboard uses PyQt5 which requires a separate environment:

```powershell
# Create dashboard-specific environment
python -m virtualenv venv_dashboard

# Activate dashboard environment
.\venv_dashboard\Scripts\Activate.ps1

# Install dashboard dependencies
pip install pandas PyQt5 PyQtChart numpy python-dateutil pytz

# Deactivate and return to main environment
deactivate
.\venv\Scripts\Activate.ps1
```

### Step 5: Verify Installation
```powershell
# Check if all packages are installed
pip list

# You should see packages like:
# - pygame
# - pandas
# - numpy
# - matplotlib
# - etc.
```

---

## 🎮 Running the Simulation

### Option 1: GUI Mode (Recommended for Development)

```powershell
# Make sure main environment is activated
.\venv\Scripts\Activate.ps1

# Run the GUI
python gui.py
```

**What to expect:**
- A window opens showing the port terminal layout
- You'll see horizontal transports (HTs) moving containers
- Real-time visualization of job execution
- You can adjust simulation speed by modifying `number_of_refresh_per_physical_second` in `gui.py`

**Controls:**
- **Close window** to stop simulation

### Option 2: CLI Mode (For Performance Testing)

```powershell
# Make sure main environment is activated
.\venv\Scripts\Activate.ps1

# Run the CLI
python cli.py
```

**What to expect:**
- Text-based progress indicators in the terminal
- Simulation runs faster without GUI overhead
- Analytics are logged to CSV files in `data/analytics_logs/`
- Results saved to `data/output.csv`
- Logs saved to `logs/` folder

**Sample Output:**
```
========================================
PSA TERMINAL SIMULATION - CLI MODE
========================================

[INFO] Loading 410 jobs from input.csv
[INFO] Starting simulation...
[DEBUG] [RECORD] Completion: QC5_0011 (DI) at H2
[INFO] [OK] Recorded 1 newly completed jobs
...
[INFO] Simulation completed in 1,167,610 seconds
```

---

## 📊 Analytics Dashboard

The analytics dashboard provides real-time insights into the simulation.

### Starting the Dashboard

**IMPORTANT**: Run the dashboard in a **separate terminal** while the simulation is running!

#### Terminal 1: Run Simulation
```powershell
# Activate main environment
.\venv\Scripts\Activate.ps1

# Run CLI simulation
python cli.py
```

#### Terminal 2: Launch Dashboard
```powershell
# Navigate to project directory
cd "c:\Users\Kiree\Desktop\OneDrive_2025-10-17\Problem Statements\Problem Statement 1 - Smart Port Operations\Simulation GUI"

# Activate dashboard environment
.\venv_dashboard\Scripts\Activate.ps1

# Launch dashboard
python launch_dashboard.py
```

**What to expect:**
- A PyQt5 window opens with analytics cards
- Dashboard auto-refreshes every 2 seconds
- Data updates as simulation progresses

### Dashboard Layout

The dashboard displays 4 main sections:

#### 1. **HT Timelines** (Top Row - Full Width)
- **Active Jobs**: Currently executing jobs
- **Completed Jobs**: Successfully finished jobs
- **Tracked Jobs**: Total jobs being monitored

#### 2. **Yard Job Counters** (Second Row - Full Width)
- **Summary Stats**: Total DI/LO job counts
- **Stacked Bar Chart**: Visual breakdown of all 16 yards showing DI (red) and LO (yellow) job distribution
- **Real-time Updates**: Counter increments as jobs complete

#### 3. **Emissions Tracker** (Bottom Left)
- **Total Emissions**: Cumulative CO2 emissions in kg
- **DI Jobs Progress Bar**: Orange bar showing remaining DI jobs (depletes to zero)
- **LO Jobs Progress Bar**: Green bar showing remaining LO jobs (depletes to zero)
- **Job Counter**: Shows "X jobs" in the middle of each bar, moving as bar depletes

#### 4. **Route Optimization** (Bottom Right)
- **Total Routes**: Number of routes analyzed
- **Avg Efficiency**: Average efficiency score (0-100%)
- **Optimal Routes**: Percentage of routes that meet optimization criteria
- **Progress Bars**: Visual representation of efficiency metrics


## 📁 Project Structure

```
Simulation GUI/
├── cli.py                          # CLI entry point
├── gui.py                          # GUI entry point
├── launch_dashboard.py             # Analytics dashboard launcher
├── requirements.txt                # Main dependencies
├── README.md                       # Original README
├── DETAILED_README.md              # This comprehensive guide
│
├── data/
│   ├── input.csv                   # Input job details
│   ├── output.csv                  # Simulation results (generated)
│   └── analytics_logs/             # Analytics CSV files (generated)
│       ├── yard_job_counts.csv     # Yard completion tracking
│       ├── ht_timelines.csv        # Job timeline data
│       ├── emissions.csv           # Emissions calculations
│       ├── emissions_summary.csv   # Emissions aggregation
│       ├── route_optimization.csv  # Route analysis
│       ├── route_summary.csv       # Route statistics
│       ├── congestion_events.csv   # Congestion tracking
│       └── congestion_alerts.csv   # Critical alerts
│
├── logs/                           # Simulation log files
│   └── simulation_YYYYMMDD_HHMMSS.log
│
├── src/
│   ├── constant.py                 # System constants
│   ├── floor.py                    # Terminal layout
│   ├── job.py                      # Job definitions
│   ├── operators.py                # HT operators
│   ├── simulation.py               # Main simulation logic
│   │
│   ├── analytics/                  # Analytics engine
│   │   ├── __init__.py
│   │   ├── analytics_engine.py     # Unified analytics (850+ lines)
│   │   └── dashboard.py            # PyQt5 dashboard
│   │
│   ├── operate/                    # Operation engine
│   │   └── engine.py               # Execution logic
│   │
│   ├── plan/                       # Planning engine ⭐ YOUR MAIN FOCUS
│   │   ├── engine.py               # Core planning logic (legacy name)
│   │   ├── planning_engine.py      # Renamed planning engine
│   │   ├── job_planner.py          # Main planner with analytics integration
│   │   └── job_tracker.py          # Job state tracking
│   │
│   ├── ui/                         # UI components
│   │   ├── draw.py                 # Drawing utilities
│   │   ├── HT.py                   # HT visualization
│   │   ├── job_progress.py         # Progress tracking
│   │   └── terminal.py             # Terminal UI
│   │
│   └── utils/                      # Utilities
│       └── logging.py              # Logging configuration
│
├── venv/                           # Main virtual environment
└── venv_dashboard/                 # Dashboard virtual environment
```

### Key Files to Understand

#### **Your Main Task: `src/plan/job_planner.py`**
This is where you'll implement your optimization algorithm. It includes:
- **Job scheduling logic**: When and how to assign jobs
- **Route planning**: Path selection for HTs
- **Resource allocation**: Managing HT availability
- **Analytics integration**: Real-time tracking of all metrics

Search for `# YOUR TASK HERE` comments in the code.

#### **Analytics Engine: `src/analytics/analytics_engine.py`**
Unified analytics module containing 5 sub-engines:
1. **YardJobCounter**: Tracks job completions per yard
2. **HTTimelineTracker**: Monitors job lifecycle events
3. **EmissionsCalculator**: Calculates CO2 emissions
4. **RouteOptimizationAnalyzer**: Evaluates route efficiency
5. **CongestionMonitor**: Detects bottlenecks

#### **Dashboard: `src/analytics/dashboard.py`**
PyQt5-based real-time monitoring interface with:
- Custom widgets (ProgressBar, StackedBarChart, DashboardCard)
- Auto-refresh mechanism
- Responsive layout system

---

## 📈 Understanding the Analytics

### 1. Yard Job Counters (`yard_job_counts.csv`)

**Purpose**: Track which jobs complete at each yard

**Columns**:
- `timestamp`: When the job completed
- `job_seq`: Job identifier (e.g., "QC5_0011")
- `job_type`: "DI" or "LO"
- `yard_name`: Which yard (H1-H16)
- `yard_total`: Running total for that yard
- `yard_di_count`: DI jobs at that yard
- `yard_lo_count`: LO jobs at that yard

**How it works**: 
- The `job_planner.py` polls the `job_tracker` for completed jobs
- Each completion is logged with timestamp and details
- Dashboard aggregates and visualizes in stacked bar chart

### 2. HT Timelines (`ht_timelines.csv`)

**Purpose**: Track the full lifecycle of each job

**Columns**:
- `timestamp`: Event time
- `job_seq`: Job identifier
- `job_type`: "DI" or "LO"
- `ht_id`: Which HT is assigned
- `event`: "created", "assigned", "started", "completed"
- `status`: "pending" or "completed"
- `location`: Current position

**How it works**:
- Timeline created when job assigned
- Updated throughout job execution
- Dashboard counts active/completed jobs

### 3. Emissions Calculator (`emissions.csv`)

**Purpose**: Calculate environmental impact

**Columns**:
- `timestamp`: Calculation time
- `job_seq`: Job identifier
- `job_type`: "DI" or "LO"
- `distance_m`: Route distance in meters
- `time_s`: Job duration in seconds
- `emissions_kg`: CO2 emissions in kilograms
- `cumulative_emissions`: Running total

**Formula**:
```
Emissions (kg) = Distance (km) × Emission_Factor  #This is a place holder formula that can be adjusted with real data, PSA can cosnider expanding into this to run simulations on collecting their scope 3 emissions as well. 
where:
- Emission_Factor_DI = 0.15 kg CO2/km
- Emission_Factor_LO = 0.12 kg CO2/km
```

**Dashboard Display**:
- Total emissions shown with DI/LO breakdown
- Separate progress bars for DI and LO jobs
- Counter shows remaining jobs in each category

### 4. Route Optimization (`route_optimization.csv`)

**Purpose**: Evaluate route quality

**Columns**:
- `timestamp`: Analysis time
- `job_seq`: Job identifier
- `route_length_m`: Actual distance traveled
- `optimal_length_m`: Theoretical shortest path
- `efficiency_pct`: (optimal / actual) × 100
- `is_optimal`: Boolean flag if efficiency > 90%

**Metrics**:
- **Efficiency Score**: How close the route is to optimal
- **Optimal Route %**: Percentage of routes meeting threshold
- **Average Efficiency**: Mean efficiency across all routes

**Dashboard Display**:
- Average efficiency progress bar (green)
- Optimal routes percentage bar (cyan)
- Summary statistics

### 5. Congestion Monitor (`congestion_events.csv`, `congestion_alerts.csv`)

**Purpose**: Detect bottlenecks and traffic issues

**Congestion Events Columns**:
- `timestamp`: When congestion detected
- `location`: Grid position
- `severity`: "LOW", "MEDIUM", "HIGH", "CRITICAL"
- `active_hts`: Number of HTs in area
- `threshold`: Congestion threshold

**Congestion Alerts** (critical events only):
- Filtered events with HIGH or CRITICAL severity
- Dashboard shows popup notifications
- Helps identify problem areas

---

## 🔍 Monitoring Your Optimization

### Key Performance Indicators (KPIs)

1. **Total Simulation Time** ⏱️
   - **Primary KPI**: Minimize this!
   - Found in CLI output and `output.csv`
   - Target: < 1,000,000 seconds

2. **Job Completion Rate** 📊
   - Track active vs completed in HT Timelines
   - Watch the progress bars deplete
   - Aim for steady, consistent completion

3. **Yard Utilization** 🏗️
   - Check yard job counter distribution
   - Avoid overloading specific yards
   - Balanced bars = good utilization

4. **Route Efficiency** 🗺️
   - Monitor average efficiency score
   - Target: > 85% optimal routes
   - Higher efficiency = shorter distances

5. **Emissions** 🌱
   - Watch total emissions accumulation
   - Compare DI vs LO emissions
   - Lower emissions = better routes

### Optimization Workflow

1. **Baseline Run**
   ```powershell
   python cli.py
   ```
   Note the simulation time and metrics

2. **Modify Algorithm**
   Edit `src/plan/job_planner.py`
   - Search for `# YOUR TASK HERE`
   - Implement your strategy
   - Save changes

3. **Test with Dashboard**
   ```powershell
   # Terminal 1
   python cli.py
   
   # Terminal 2 (separate PowerShell)
   .\venv_dashboard\Scripts\Activate.ps1
   python launch_dashboard.py
   ```
   Watch real-time impact of your changes

4. **Compare Results**
   - Check simulation time reduction
   - Review analytics CSV files
   - Validate improvements in dashboard

5. **Iterate**
   Repeat steps 2-4 until satisfied

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### ❌ Issue: "Python not recognized"
**Solution**:
```powershell
# Add Python to PATH or use full path
C:\Python311\python.exe --version
```

#### ❌ Issue: "Cannot activate virtual environment"
**Solution**:
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
.\venv\Scripts\Activate.ps1
```

#### ❌ Issue: "ModuleNotFoundError: No module named 'PyQt5'"
**Solution**:
```powershell
# Make sure dashboard environment is activated
.\venv_dashboard\Scripts\Activate.ps1

# Reinstall PyQt5
pip install PyQt5 PyQtChart
```

#### ❌ Issue: "Dashboard shows 'No data available yet'"
**Solution**:
- Ensure CLI simulation is running in another terminal
- Check that `data/analytics_logs/` folder exists
- Wait a few seconds for data generation
- Verify CSV files are being created in `data/analytics_logs/`

#### ❌ Issue: "Simulation time not improving"
**Solution**:
- Review your algorithm logic in `job_planner.py`
- Check for inefficient loops or calculations
- Analyze route optimization metrics
- Review congestion events for bottlenecks
- Consider parallelization strategies

#### ❌ Issue: "Dashboard freezes or doesn't update"
**Solution**:
```powershell
# Close dashboard (X button)
# Check if simulation is still running
# Restart dashboard
python launch_dashboard.py
```

#### ❌ Issue: "Import errors in job_planner.py"
**Solution**:
```powershell
# Verify analytics engine exists
dir src\analytics\analytics_engine.py

# If missing, check that consolidation was successful
# The file should be ~850 lines
```

### Debug Mode

Enable verbose logging:
```python
# In cli.py or gui.py, add at the top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Checking Analytics Data

```powershell
# View analytics files
dir data\analytics_logs\

# Count rows in a CSV
python -c "import pandas as pd; print(len(pd.read_csv('data/analytics_logs/yard_job_counts.csv')))"

# Quick data check
python -c "import pandas as pd; df = pd.read_csv('data/analytics_logs/emissions.csv'); print(df.head())"
```

```text
Team Name: [Your Team Name]
Optimization Strategy: [Brief description]

===== INSTALLATION =====
1. Copy job_planner.py to src/plan/
2. [Any additional steps]

===== RUNNING =====
# Activate environment
.\venv\Scripts\Activate.ps1

# Run simulation
python cli.py

# Launch dashboard (separate terminal)
.\venv_dashboard\Scripts\Activate.ps1
python launch_dashboard.py

===== IMPROVEMENTS =====
- Simulation Time: [X seconds] → [Y seconds] ([Z]% improvement)
- Route Efficiency: [X]% → [Y]%
- Avg Emissions: [X kg] → [Y kg]

===== KEY CHANGES =====
1. [List major algorithmic changes]
2. [Explain optimization techniques]
3. [Document any new features]

===== DEPENDENCIES =====
[List any new packages if added]
```

### Performance Benchmarks to Report

Include these metrics in your presentation:

| Metric | Baseline | Your Solution | Improvement |
|--------|----------|---------------|-------------|
| Total Simulation Time | 1,167,610s | ? | ?% |
| Average Route Efficiency | ?% | ?% | ?% |
| Total Emissions | ? kg | ? kg | ?% |
| Optimal Routes % | ?% | ?% | ?% |
| Yard Balance (std dev) | ? | ? | ?% |

### Dashboard Screenshots to Include

1. **Overview**: Full dashboard showing all 4 cards
2. **Yard Distribution**: Stacked bar chart closeup
3. **Emissions Progress**: DI/LO progress bars with counters
4. **Route Efficiency**: Efficiency metrics
5. **Comparison**: Before/after metrics side-by-side

---

## 🎓 Additional Resources

### Understanding the Codebase

- **Planning Engine**: `src/plan/job_planner.py` - Your main focus
- **Job Tracker**: `src/plan/job_tracker.py` - State management
- **Analytics**: `src/analytics/analytics_engine.py` - Metrics calculation
- **Dashboard**: `src/analytics/dashboard.py` - Visualization

### Optimization Strategies to Consider

1. **Job Prioritization**
   - Critical jobs first
   - Distance-based sorting
   - Yard load balancing

2. **Route Planning**
   - A* pathfinding
   - Avoiding congested areas
   - Pre-computed route caching

3. **Resource Allocation**
   - Nearest HT assignment
   - Load balancing across HTs
   - Predictive assignment

4. **Congestion Management**
   - Dynamic re-routing
   - Wait queue strategies
   - Traffic flow optimization

### Analytics Integration

Your `job_planner.py` already integrates with analytics:
```python
# In __init__:
self.analytics = AnalyticsEngine(folder)

# When job completes:
self.analytics.record_job_completion(...)
self.analytics.complete_job_timeline(...)

# When planning route:
self.analytics.create_timeline(...)
self.analytics.calculate_emissions(...)
self.analytics.analyze_route(...)
```

---

## 📞 Support

For questions or issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review log files in `logs/`
3. Inspect analytics CSV files for data issues
4. Contact your CodeSprint organizers

---

## ✅ Quick Start Checklist

- [ ] Python 3.10/3.11 installed
- [ ] Project directory navigated to
- [ ] Main venv created and activated
- [ ] Dependencies installed via pip-sync
- [ ] Dashboard venv created
- [ ] PyQt5 installed in dashboard venv
- [ ] CLI runs successfully: `python cli.py`
- [ ] Dashboard launches: `python launch_dashboard.py`
- [ ] Analytics CSV files generated in `data/analytics_logs/`
- [ ] Dashboard shows live data
- [ ] Baseline metrics recorded
- [ ] Ready to optimize!

---

You now have everything you need to:
- ✅ Run the simulation (CLI & GUI)
- ✅ Monitor with analytics dashboard
- ✅ Understand all metrics and data

