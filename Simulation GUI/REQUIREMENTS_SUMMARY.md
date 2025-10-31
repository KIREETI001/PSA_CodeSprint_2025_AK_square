# Requirements Summary - PSA Terminal Simulation

## Overview
The `requirements.txt` file contains all dependencies needed to run all components of the PSA Terminal Simulation project.

## Core Dependencies (Required for All Components)

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥2.0.0 | Data processing and analytics |
| numpy | ≥1.24.0 | Numerical computations |
| logzero | ≥1.7.0 | Enhanced logging |
| colorama | ≥0.4.6 | Colored terminal output |

## Dashboard Dependencies (PyQt5 Real-time Analytics)

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | ≥5.15.0 | GUI framework for dashboard |
| PyQtChart | ≥5.15.0 | Chart widgets for visualizations |

**Entry Point:** `launch_dashboard.py`

## GUI Dependencies (pygame-zero Visualization)

| Package | Version | Purpose |
|---------|---------|---------|
| pgzero | ≥1.2.0 | pygame-zero framework |
| pygame | ≥2.0.0 | Game/graphics library |

**Entry Point:** `gui.py`

## Data Processing Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| openpyxl | ≥3.0.0 | Excel file handling |
| python-dateutil | ≥2.8.0 | Date/time parsing |
| pytz | ≥2021.1 | Timezone support |

## Installation Matrix

### Full Installation (All Features)
```bash
pip install -r requirements.txt
```
**Installs:** CLI + Dashboard + GUI + Analytics

**Size:** ~150MB (includes PyQt5, pygame, pandas, numpy, and all dependencies)

### Minimal Installation (CLI Only)
```bash
pip install pandas numpy logzero colorama
```
**Size:** ~50MB (pandas + numpy + minimal deps)

### Dashboard Only
```bash
pip install pandas numpy logzero PyQt5 PyQtChart
```
**Size:** ~100MB (includes PyQt5 framework)

### GUI Only
```bash
pip install pandas numpy logzero pgzero pygame
```
**Size:** ~80MB (includes pygame and SDL libraries)

## Verified Environment

Tested and verified on:
- **Python:** 3.10.9
- **OS:** Windows 10/11
- **Virtual Environment:** venv_dashboard

### Actual Installed Versions (as of verification)
```
Python 3.10.9
pandas 2.3.3
numpy 2.2.6
logzero 1.7.0
PyQt5 5.15.11
pygame 2.6.1
pgzero 1.2.1
colorama 0.4.6
openpyxl 3.1.5
python-dateutil 2.9.0
pytz 2025.2
```

## Development Dependencies (Optional)

Commented out in `requirements.txt` by default. Uncomment to enable:

| Package | Purpose |
|---------|---------|
| black | Code formatting |
| isort | Import sorting |
| invoke | Task automation |
| notebook | Jupyter notebooks |
| ipykernel | Jupyter Python kernel |

## Dependency Tree Summary

```
PSA Terminal Simulation
├── Core Simulation
│   ├── pandas (data processing)
│   ├── numpy (numerical ops)
│   ├── logzero (logging)
│   └── colorama (terminal colors)
├── Dashboard (launch_dashboard.py)
│   ├── PyQt5 (GUI framework)
│   └── PyQtChart (charts)
├── GUI (gui.py)
│   ├── pgzero (game framework)
│   └── pygame (graphics engine)
└── Analytics
    ├── openpyxl (Excel export)
    ├── python-dateutil (date handling)
    └── pytz (timezones)
```

## Compatibility Notes

### Python Version
- **Minimum:** Python 3.10
- **Recommended:** Python 3.10.9 or 3.11.x
- **Maximum:** Python 3.12.x (some packages may require updates)

### Operating Systems

| OS | CLI | Dashboard | GUI | Status |
|----|-----|-----------|-----|--------|
| Windows 10/11 | ✅ | ✅ | ✅ | Fully supported |
| macOS | ✅ | ✅ | ⚠️ | GUI may need config |
| Linux | ✅ | ✅ | ⚠️ | GUI may need config |

### Known Issues
1. **pgzero import in interactive Python:** Expected behavior - only works when running files
2. **PyQt5 on macOS:** May require `python.app` framework build
3. **pygame on Linux:** May require SDL2 system libraries

## Installation Time Estimates

| Installation Type | Download Size | Install Time (avg) |
|------------------|---------------|-------------------|
| Full (all deps) | ~150 MB | 2-5 minutes |
| Core + Dashboard | ~100 MB | 2-4 minutes |
| Core + GUI | ~80 MB | 1-3 minutes |
| Core only | ~50 MB | 1-2 minutes |

*Times based on typical broadband connection and modern hardware*

## Upgrade Path

To upgrade all dependencies to latest compatible versions:
```bash
pip install --upgrade -r requirements.txt
```

To freeze exact versions for reproducibility:
```bash
pip freeze > requirements-lock.txt
```

## Next Steps

1. **Install:** Follow `INSTALLATION.md` for detailed setup instructions
2. **Verify:** Run the verification commands to confirm installation
3. **Run:** Use the appropriate entry point for your needs:
   - CLI: `python cli.py`
   - Dashboard: `python launch_dashboard.py`
   - GUI: `python gui.py`

## Support

For dependency-related issues:
1. Check `INSTALLATION.md` for troubleshooting
2. Verify Python version: `python --version`
3. Ensure virtual environment is activated
4. Try reinstalling: `pip install --force-reinstall -r requirements.txt`
