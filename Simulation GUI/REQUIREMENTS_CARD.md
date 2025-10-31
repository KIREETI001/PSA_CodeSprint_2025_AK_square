# Requirements.txt - Package Reference

## One-Line Install
```bash
pip install -r requirements.txt
```

## What's Included

### Core (Always Required)
```
pandas>=2.0.0       # Data processing
numpy>=1.24.0       # Numerical ops
logzero>=1.7.0      # Logging
colorama>=0.4.6     # Terminal colors
```

### Dashboard
```
PyQt5>=5.15.0       # GUI framework
PyQtChart>=5.15.0   # Charts
```

### GUI
```
pgzero>=1.2.0       # Game framework
pygame>=2.0.0       # Graphics
```

### Data Export
```
openpyxl>=3.0.0         # Excel files
python-dateutil>=2.8.0  # Dates
pytz>=2021.1            # Timezones
```

## Component-Specific Install

### CLI Only
```bash
pip install pandas numpy logzero colorama
```

### Dashboard Only
```bash
pip install pandas numpy logzero PyQt5 PyQtChart
```

### GUI Only
```bash
pip install pandas numpy logzero pgzero pygame
```

## Verified Versions (venv_dashboard)
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
```

## Quick Verification
```bash
python -c "import pandas, numpy, logzero; print('Core OK')"
python -c "from PyQt5.QtWidgets import QApplication; print('Dashboard OK')"
python -c "import pgzero, pygame; print('GUI OK')"
```

## Total Size
~150 MB (all dependencies)

## Links
- Full details: [REQUIREMENTS_SUMMARY.md](REQUIREMENTS_SUMMARY.md)
- Installation help: [INSTALLATION.md](INSTALLATION.md)
- Quick start: [QUICKSTART.md](QUICKSTART.md)
