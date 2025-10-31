# Quick Start Guide

## 5-Minute Setup

### 1️⃣ Install Python 3.10+
Download from [python.org](https://www.python.org/downloads/)

### 2️⃣ Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4️⃣ Run Your First Simulation
```powershell
# Option A: Visual GUI
python gui.py

# Option B: Fast CLI
python cli.py

# Option C: Analytics Dashboard
python launch_dashboard.py
```

## That's It! 🎉

---

## What Next?

### Monitor in Real-Time
Run dashboard + simulation simultaneously:

**Terminal 1:**
```powershell
python launch_dashboard.py
```

**Terminal 2:**
```powershell
python cli.py
```

Watch live analytics as simulation runs!

### Optimize the Algorithm

1. Open `src/plan/job_planner.py`
2. Find `# YOUR TASK HERE` comments
3. Modify the planning logic
4. Run `python cli.py` to test
5. Check `data/output.csv` for improved times

**Goal:** Minimize total simulation time!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Import errors | Activate venv: `.\venv\Scripts\Activate.ps1` |
| Dashboard won't start | Check PyQt5: `pip install PyQt5 PyQtChart` |
| GUI crashes | Check pygame: `pip install pygame pgzero` |

**Still stuck?** See [INSTALLATION.md](INSTALLATION.md) for detailed help.

---

## Project Overview

```
📦 PSA Terminal Simulation
├── 🎮 gui.py              # Interactive visualization
├── 💻 cli.py              # Headless simulation
├── 📊 launch_dashboard.py # Real-time analytics
└── 📁 src/
    ├── plan/
    │   └── job_planner.py # ⭐ YOUR CODE GOES HERE
    └── analytics/
        └── dashboard.py   # Live dashboard
```

---

## Key Files

| File | Purpose |
|------|---------|
| `requirements.txt` | All dependencies (one-click install) |
| `data/input.csv` | Input job data |
| `data/output.csv` | Simulation results (generated) |
| `data/analytics_logs/` | Real-time metrics (auto-created) |
| `logs/` | Detailed simulation logs |

---

## Common Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run GUI
python gui.py

# Run CLI (headless)
python cli.py

# Launch dashboard
python launch_dashboard.py

# Verify installation
python -c "import pandas, numpy, PyQt5, pgzero; print('✓ All OK')"

# Deactivate environment
deactivate
```

---

## Performance Testing

```powershell
# Run simulation
python cli.py

# Check results
# Look for final time in terminal output or data/output.csv
```

**Baseline:** ~1,167,610 seconds (example)  
**Your Goal:** Beat the baseline! 🏆

---

## Need Help?

📖 **Detailed Docs:**
- [INSTALLATION.md](INSTALLATION.md) - Complete setup guide
- [REQUIREMENTS_SUMMARY.md](REQUIREMENTS_SUMMARY.md) - Dependency info
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
- [README.md](README.md) - Full project documentation

💡 **Tip:** Run `python gui.py` first to see the simulation in action!

---

## Component Matrix

| Feature | GUI | CLI | Dashboard |
|---------|-----|-----|-----------|
| Visual feedback | ✅ | ❌ | ✅ |
| Speed | 🐢 Slow | 🚀 Fast | 🐢 Slow |
| Analytics | Basic | CSV | Full |
| Best for | Development | Testing | Monitoring |

**Recommended Workflow:**
1. Develop with GUI (`gui.py`) for visual feedback
2. Test with CLI (`cli.py`) for performance
3. Monitor with Dashboard during long runs

---

## Version Info

- **Python:** 3.10.9+ (tested)
- **OS:** Windows 10/11 (recommended)
- **Dependencies:** See `requirements.txt`

---

## Success Checklist

- [x] Python 3.10+ installed
- [x] Virtual environment created
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Can run `python gui.py` successfully
- [x] Can run `python cli.py` successfully
- [x] Can run `python launch_dashboard.py` successfully
- [x] Understand where to edit code (`src/plan/job_planner.py`)
- [x] Know how to check results (`data/output.csv`)

**All checked?** You're ready to optimize! 🚀

---

*Last updated: October 20, 2025*
