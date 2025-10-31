# Installation Guide - PSA Terminal Simulation

## Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Windows OS (for GUI features)

### 2. Install Dependencies

```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
# OR
.\venv\Scripts\activate.bat    # Command Prompt

# Install all dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test imports
python -c "import pandas, numpy, logzero; print('✓ Core dependencies OK')"
python -c "from PyQt5.QtWidgets import QApplication; print('✓ Dashboard dependencies OK')"
python -c "import pgzero, pygame; print('✓ GUI dependencies OK')"
```

## Component-Specific Requirements

### Core Simulation & CLI Only
If you only need the CLI simulation (no GUI or dashboard):
```bash
pip install pandas numpy logzero colorama
```

### Dashboard Only
For the real-time analytics dashboard:
```bash
pip install pandas numpy logzero PyQt5 PyQtChart
```

### GUI Visualization Only
For the pygame-zero GUI:
```bash
pip install pandas numpy logzero pgzero pygame
```

## Running the Project

### CLI Simulation
```bash
python cli.py
```

### Analytics Dashboard (separate terminal)
```bash
python launch_dashboard.py
```

### GUI Visualization
```bash
python gui.py
```

### Run Both Dashboard + CLI Simultaneously
```powershell
# Terminal 1: Start dashboard
python launch_dashboard.py

# Terminal 2: Run simulation (generates analytics)
python cli.py
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Ensure you've activated the virtual environment and installed requirements:
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: pgzrun import error in interactive mode
**Solution:** This is expected behavior. `pgzrun` only works when running files, not in interactive Python.

### Issue: PyQt5 not found
**Solution:** Install PyQt5 explicitly:
```bash
pip install PyQt5 PyQtChart
```

### Issue: pygame/pgzero issues
**Solution:** Reinstall pygame and pgzero:
```bash
pip uninstall pygame pgzero -y
pip install pygame pgzero
```

## Data Requirements

The simulation requires:
- `data/input.csv` - Job input data
- `data/analytics_logs/` - Created automatically for analytics output

Sample data structure:
```
data/
├── input.csv          # Input jobs
├── output.csv         # Simulation results
└── analytics_logs/    # Real-time analytics CSVs
    ├── congestion_alerts.csv
    ├── emissions_summary.csv
    ├── route_optimization.csv
    ├── yard_summary.csv
    └── ...
```

## Development Setup (Optional)

For development with Jupyter notebooks and code formatting:

1. Uncomment the development tools section in `requirements.txt`
2. Install:
   ```bash
   pip install -r requirements.txt
   ```

3. Tools included:
   - `black` - Code formatter
   - `isort` - Import organizer
   - `invoke` - Task runner
   - `notebook` - Jupyter notebooks
   - `ipykernel` - Jupyter kernel

## Platform Notes

### Windows
All features fully supported. PyQt5 dashboard and pygame GUI work out of the box.

### macOS / Linux
- Dashboard (PyQt5): Fully supported
- CLI: Fully supported
- GUI (pygame): May require additional configuration for window management

## Version Information

Minimum tested versions:
- Python: 3.10.9
- pandas: 2.0.0
- numpy: 1.24.0
- PyQt5: 5.15.0
- pgzero: 1.2.0
- pygame: 2.0.0

For exact versions used in development, see the previous `requirements.txt` comments or use:
```bash
pip freeze > requirements-lock.txt
```
