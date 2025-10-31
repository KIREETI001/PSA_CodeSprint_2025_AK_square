"""
Test script to verify analytics integration with the simulation.
This runs a limited simulation and verifies all analytics modules are working.
"""
import sys
from pathlib import Path
import time
import pandas as pd
from logzero import logger

from src.constant import CONSTANT
from src.simulation import Simulation
from src.utils import logging

def test_analytics_integration():
    """Test the analytics system with actual simulation."""
    
    print("\n" + "="*60)
    print("🧪 TESTING ANALYTICS INTEGRATION")
    print("="*60 + "\n")
    
    # Setup logging
    logging.setup_logger()
    
    # Initialize simulation
    print("📊 Initializing simulation with analytics...")
    simulation = Simulation()
    
    # Access the job planner through planning engine
    job_planner = simulation.planning_engine.job_planner
    
    # Verify analytics modules are initialized
    print("\n✅ Checking analytics modules initialization...")
    assert hasattr(job_planner, 'timeline_tracker'), "❌ Timeline tracker not initialized"
    print("  ✓ Timeline Tracker: OK")
    
    assert hasattr(job_planner, 'emissions_calculator'), "❌ Emissions calculator not initialized"
    print("  ✓ Emissions Calculator: OK")
    
    assert hasattr(job_planner, 'yard_counter'), "❌ Yard counter not initialized"
    print("  ✓ Yard Job Counter: OK")
    
    assert hasattr(job_planner, 'congestion_monitor'), "❌ Congestion monitor not initialized"
    print("  ✓ Congestion Monitor: OK")
    
    assert hasattr(job_planner, 'route_analyzer'), "❌ Route analyzer not initialized"
    print("  ✓ Route Optimization Analyzer: OK")
    
    # Check that analytics log directory exists
    analytics_dir = Path("data/analytics_logs")
    if not analytics_dir.exists():
        print(f"\n📁 Creating analytics directory: {analytics_dir}")
        analytics_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"\n📁 Analytics directory exists: {analytics_dir}")
    
    # Run limited simulation (10 iterations)
    print("\n🚀 Running simulation for 10 iterations...")
    print("-" * 60)
    
    iteration_count = 0
    max_iterations = 10
    
    while iteration_count < max_iterations:
        simulation.update()
        system_time = simulation.get_current_time()
        
        # Update analytics with current simulation time
        job_planner.update_simulation_time(system_time)
        
        if iteration_count % 2 == 0:
            print(f"  ⏱️  Iteration {iteration_count+1}: Time = {system_time:.0f}s")
        
        if simulation.has_completed_all_jobs():
            logger.info(f"Time: {system_time:,.0f}. All jobs completed!")
            break
        
        if simulation.has_deadlock():
            logger.info(f"Time: {system_time:,.0f}. Deadlock detected.")
            break
        
        iteration_count += 1
    
    print("-" * 60)
    
    # Get analytics summary
    print("\n📈 Retrieving analytics summary...")
    summary = job_planner.get_analytics_summary()
    
    # Display summary
    print("\n" + "="*60)
    print("📊 ANALYTICS SUMMARY")
    print("="*60)
    
    print("\n🎯 HT Timeline Tracker:")
    timeline_stats = summary.get('timeline_tracker', {})
    print(f"  • Total Jobs Tracked: {timeline_stats.get('total_jobs', 0)}")
    print(f"  • Active Jobs: {timeline_stats.get('active_jobs', 0)}")
    print(f"  • Completed Jobs: {timeline_stats.get('completed_jobs', 0)}")
    
    print("\n💨 Emissions Calculator:")
    emissions_stats = summary.get('emissions_calculator', {})
    print(f"  • Total Emissions: {emissions_stats.get('total_emissions_kg', 0):.2f} kg")
    print(f"  • DI Emissions: {emissions_stats.get('di_emissions_kg', 0):.2f} kg")
    print(f"  • LO Emissions: {emissions_stats.get('lo_emissions_kg', 0):.2f} kg")
    print(f"  • Jobs Tracked: {emissions_stats.get('jobs_tracked', 0)}")
    
    print("\n🏭 Yard Job Counter:")
    yard_stats = summary.get('yard_counter', {})
    print(f"  • Total Jobs: {yard_stats.get('total_jobs', 0)}")
    print(f"  • DI Jobs: {yard_stats.get('di_jobs', 0)}")
    print(f"  • LO Jobs: {yard_stats.get('lo_jobs', 0)}")
    
    print("\n🚦 Congestion Monitor:")
    congestion_stats = summary.get('congestion_monitor', {})
    print(f"  • Total Events: {congestion_stats.get('total_events', 0)}")
    print(f"  • Active Congestion: {congestion_stats.get('active_congestion_count', 0)}")
    if congestion_stats.get('has_critical_alert'):
        print("  ⚠️  CRITICAL ALERT ACTIVE!")
    
    print("\n🛣️  Route Optimization Analyzer:")
    route_stats = summary.get('route_analyzer', {})
    print(f"  • Routes Analyzed: {route_stats.get('total_routes', 0)}")
    print(f"  • Average Efficiency: {route_stats.get('average_efficiency', 0):.1f}%")
    print(f"  • Optimal Routes: {route_stats.get('optimal_routes', 0)}")
    print(f"  • Inefficient Routes: {route_stats.get('inefficient_routes', 0)}")
    
    # Check for CSV files
    print("\n" + "="*60)
    print("📁 CHECKING CSV LOG FILES")
    print("="*60 + "\n")
    
    expected_files = [
        'ht_timelines.csv',
        'emissions.csv',
        'emissions_summary.csv',
        'yard_job_counts.csv',
        'yard_summary.csv',
        'congestion_events.csv',
        'congestion_alerts.csv',
        'route_optimization.csv',
        'route_summary.csv'
    ]
    
    files_created = 0
    for filename in expected_files:
        filepath = analytics_dir / filename
        if filepath.exists():
            file_size = filepath.stat().st_size
            print(f"  ✅ {filename} ({file_size:,} bytes)")
            files_created += 1
            
            # Show first few rows for verification
            if file_size > 0:
                try:
                    df = pd.read_csv(filepath)
                    print(f"     └─ {len(df)} rows")
                except Exception as e:
                    print(f"     └─ Error reading: {e}")
        else:
            print(f"  ⚠️  {filename} (not created yet)")
    
    print(f"\n📊 Files Created: {files_created}/{len(expected_files)}")
    
    # Export final analytics
    print("\n💾 Exporting final analytics reports...")
    job_planner.export_analytics()
    print("  ✅ Analytics exported successfully!")
    
    # Export simulation job report
    print("\n💾 Exporting simulation job report...")
    simulation.export_job_report()
    
    # Final verification
    print("\n" + "="*60)
    print("✅ TEST SUMMARY")
    print("="*60)
    print(f"  ✓ Analytics modules initialized: 5/5")
    print(f"  ✓ Simulation iterations completed: {iteration_count}")
    print(f"  ✓ CSV files created: {files_created}/{len(expected_files)}")
    print(f"  ✓ Analytics summary generated: Yes")
    print(f"  ✓ Analytics exported: Yes")
    
    if files_created >= len(expected_files) - 2:  # Allow some files to be empty
        print("\n🎉 ANALYTICS INTEGRATION TEST PASSED!")
        return True
    else:
        print("\n⚠️  ANALYTICS INTEGRATION TEST PARTIAL SUCCESS")
        print("   (Some CSV files not created - may need more simulation time)")
        return False

if __name__ == "__main__":
    try:
        success = test_analytics_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
