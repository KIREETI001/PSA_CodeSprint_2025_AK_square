"""Test script to verify yard counter polling mechanism"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulation import Simulation

def run_test():
    print("=== Testing Yard Counter Fix ===")
    print("\n1. Setting up simulation...")
    
    # Initialize simulation
    simulation = Simulation()
    
    print("   [OK] Simulation initialized")
    
    # Verify job_planner has the polling mechanism
    if hasattr(simulation.planning_engine.job_planner, '_check_and_record_completed_jobs'):
        print("   [OK] JobPlanner has polling mechanism for completed jobs")
    else:
        print("   [X] JobPlanner missing polling mechanism!")
        return False
    
    print("\n2. Running simulation for 500 iterations...")
    print("   (This will take a few minutes - jobs need time to complete)")
    
    for i in range(500):
        if i % 50 == 0:
            total_jobs = len(simulation.planning_engine.job_tracker.job_sequence_map)
            in_progress = sum(1 for j in simulation.planning_engine.job_tracker.job_sequence_map.values() 
                            if j.get_job_info().get("job_status").name != "COMPLETED")
            print(f"   Iteration {i}/500 - Total jobs: {total_jobs}, In progress: {in_progress}")
        simulation.update()
    
    print("\n3. Checking yard_job_counts.csv...")
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'analytics_logs', 'yard_job_counts.csv')
    
    if not os.path.exists(csv_path):
        print(f"   [X] CSV file not found: {csv_path}")
        return False
    
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    row_count = len(lines) - 1  # Minus header
    
    if row_count > 0:
        print(f"   [OK] SUCCESS! yard_job_counts.csv has {row_count} rows!")
        print(f"   Sample data (first 5 rows):")
        for line in lines[:6]:  # Header + 5 rows
            print(f"      {line.strip()}")
        return True
    else:
        print(f"   [X] FAILED! yard_job_counts.csv still has 0 rows")
        print(f"   Total jobs in tracker: {len(simulation.planning_engine.job_tracker.job_sequence_map)}")
        return False

if __name__ == "__main__":
    try:
        success = run_test()
        if success:
            print("\n=== TEST PASSED ===")
            sys.exit(0)
        else:
            print("\n=== TEST FAILED ===")
            sys.exit(1)
    except Exception as e:
        print(f"\n[X] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
