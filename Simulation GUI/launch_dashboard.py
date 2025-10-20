"""
Launch the analytics dashboard separately to monitor the simulation in real-time.
Run this in a separate terminal while the simulation is running.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analytics.dashboard import launch_dashboard

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 PSA TERMINAL ANALYTICS DASHBOARD")
    print("="*60)
    print("\nStarting dashboard...")
    print("Dashboard will refresh every 2 seconds")
    print("Close the window to exit")
    print("\n" + "="*60 + "\n")
    
    analytics_logs_path = Path("data/analytics_logs")
    
    # Create directory if it doesn't exist
    if not analytics_logs_path.exists():
        print(f"⚠️  Analytics logs directory not found: {analytics_logs_path}")
        print("Creating directory...")
        analytics_logs_path.mkdir(parents=True, exist_ok=True)
    
    try:
        launch_dashboard(analytics_logs_path)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
