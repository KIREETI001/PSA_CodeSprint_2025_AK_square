# PSA CodeSprint 2025: Smart Port Operations – AI for Horizontal Transport Optimisation (Node)

Design an AI-driven scheduling and routing strategy to minimize congestion, balance yard utilization and improve overall efficiency.

## Environment Setup

### Quick Start (Recommended)

```powershell
# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.10 or higher
- Windows 10/11 (recommended for full GUI support)

See **[INSTALLATION.md](INSTALLATION.md)** for detailed setup instructions and troubleshooting.

### What Gets Installed

The `requirements.txt` includes dependencies for:
- **Core Simulation & CLI** - pandas, numpy, logzero
- **Dashboard (PyQt5)** - Real-time analytics visualization
- **GUI (pygame-zero)** - Interactive simulation display
- **Data Export** - openpyxl for Excel reports

See **[REQUIREMENTS_SUMMARY.md](REQUIREMENTS_SUMMARY.md)** for complete dependency information.

### Alternative: Advanced Setup

If you prefer pip-tools for dependency management:

```shell
# Create virtual environment
python -m pip install virtualenv
python -m virtualenv venv
.\venv\Scripts\activate

# Install pip-tools
python -m pip install pip-tools

# Compile from requirements.in (if modifying dependencies)
pip-compile requirements.in -o requirements.txt

# Install
pip-sync requirements.txt
```

## Development

### Running the Simulation

The project offers three ways to run the simulation:

#### 1. GUI Visualization (Interactive)
```shell
python gui.py
```
Launches a pygame-zero window showing real-time port operations with visual feedback.

#### 2. CLI Simulation (Headless)
```shell
python cli.py
```
Runs simulation without GUI for faster batch execution. Outputs:
- `data/output.csv` - Job completion results
- `logs/` - Detailed simulation logs
- **Optimization Metric:** Total simulation time (minimize this!)

#### 3. Real-time Analytics Dashboard
```shell
python launch_dashboard.py
```
Launches a PyQt5 dashboard displaying live analytics. **Run in parallel with CLI:**

```powershell
# Terminal 1: Start dashboard
python launch_dashboard.py

# Terminal 2: Run simulation
python cli.py
```

The dashboard monitors:
- Job completion rates
- HT utilization and congestion
- Route optimization metrics
- Emissions tracking
- Yard density patterns

### About the Code Base

The simulation consists of two main components:

- **Planning Engine**: Where scheduling and navigating algorithms are implemented.
- **Operation Engine**: Simulates execution of planned jobs.

Your task is to improve the default planning algorithm in the Planning Engine for better performance.

### Project Structure

```
INA_DS_CS/
│
├── data/
│ └── input.csv # Input job details for the planning algorithm
├── logs/       # Log files for each simulation run
├── src/        # Source code
│ └── operate/
│ ├── plan/
| |  └── job_planner.py # Your main implementation goes here!
│ ├── ui/
│ └── utils/
├── cli.py      # Command-line interface entry point
└── gui.py      # GUI interface entry point
```

- `input.csv` contains the job details fed into the planning algorithm.
- `job_planner.py` is the core of the Planning Engine — your modifications should be made here (Search for **YOUR TASK HERE**). Refer to the provided documentation for details on the default algorithm logic.
- `gui.py` runs the simulation with a graphical interface so you can observe and fine-tune your algorithm. You can adjust `number_of_refresh_per_physical_second` in the code to control simulation speed.
- `cli.py` runs the simulation without GUI for faster batch execution. It outputs `output.csv` in the data folder and logs in `logs/`.

### Running the CLI simulation

Run the headless simulation for performance testing:

```
python cli.py
```

The simulation may take a few minutes. At the end, it will report the total simulation time (e.g., 1,167,610 seconds) — **this is the key metric you need to optimize and reduce**. Note that this is the simulation time when system checks for all job completion condition. A precise time of the last job completion can be found in `end_time` column of `output.csv` file.

## Quick Reference

| Component | Command | Purpose | Output |
|-----------|---------|---------|--------|
| **GUI** | `python gui.py` | Interactive visualization | Visual window |
| **CLI** | `python cli.py` | Headless simulation | `output.csv`, logs |
| **Dashboard** | `python launch_dashboard.py` | Live analytics | PyQt5 dashboard |
| **Combined** | Dashboard + CLI | Real-time monitoring | Both outputs |

**Files:**
- `requirements.txt` - All dependencies
- `INSTALLATION.md` - Setup guide
- `REQUIREMENTS_SUMMARY.md` - Dependency details
- `TESTING_GUIDE.md` - Validation procedures
- `VERIFICATION_REPORT.md` - Quality assurance

**Key Directories:**
- `src/plan/job_planner.py` - **YOUR IMPLEMENTATION** (search for "YOUR TASK HERE")
- `src/analytics/` - Analytics engine and dashboard
- `data/input.csv` - Input jobs
- `data/analytics_logs/` - Real-time CSV outputs

## Submission Guidelines

When you are ready to submit your solution, please prepare the following:

1. YouTube Presentation video explaining your solution.
2. PowerPoint Slides supporting your presentation.
3. Source Code:
   - Modified `job_planner.py` plus any supporting scripts that depend only on `job_planner.py`.
   - Other modifications outside of this are not allowed.
   - Zip these files into Codes_TeamName.zip.
   - Include a `README.txt` describing how to run your code and integrate it into the existing codebase.
4. Simulation Results:
   - `data/output.csv`
   - the latest log file from `logs/` demonstrating your improved results.
5. Team Photos.

---

If you have any questions or need assistance, feel free to reach out. Good luck and happy coding!
