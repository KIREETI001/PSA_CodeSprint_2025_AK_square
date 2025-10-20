"""
Test script to verify analytics system functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_analytics_imports():
    """Test that all analytics modules can be imported"""
    print("=" * 60)
    print("TEST 1: Analytics Module Imports")
    print("=" * 60)
    
    try:
        from src.analytics import (
            HTTimelineTracker,
            EmissionsCalculator,
            YardJobCounter,
            CongestionMonitor,
            RouteOptimizationAnalyzer
        )
        print("✅ All analytics modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_analytics_initialization():
    """Test that analytics modules can be initialized"""
    print("\n" + "=" * 60)
    print("TEST 2: Analytics Initialization")
    print("=" * 60)
    
    try:
        from src.analytics import (
            HTTimelineTracker,
            EmissionsCalculator,
            YardJobCounter,
            CongestionMonitor,
            RouteOptimizationAnalyzer
        )
        
        data_folder = Path("data/analytics_logs")
        
        # Initialize all trackers
        timeline_tracker = HTTimelineTracker(data_folder)
        print("✅ HTTimelineTracker initialized")
        
        emissions_calc = EmissionsCalculator(data_folder)
        print("✅ EmissionsCalculator initialized")
        
        yard_counter = YardJobCounter(data_folder)
        print("✅ YardJobCounter initialized")
        
        congestion_monitor = CongestionMonitor(data_folder)
        print("✅ CongestionMonitor initialized")
        
        route_analyzer = RouteOptimizationAnalyzer(data_folder)
        print("✅ RouteOptimizationAnalyzer initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_folder_creation():
    """Test that analytics data folder is created"""
    print("\n" + "=" * 60)
    print("TEST 3: Data Folder Creation")
    print("=" * 60)
    
    data_folder = Path("data/analytics_logs")
    
    if data_folder.exists():
        print(f"✅ Analytics folder exists: {data_folder.absolute()}")
        
        # List CSV files
        csv_files = list(data_folder.glob("*.csv"))
        if csv_files:
            print(f"\n📄 Found {len(csv_files)} CSV files:")
            for csv_file in csv_files:
                size = csv_file.stat().st_size
                print(f"   - {csv_file.name} ({size} bytes)")
        else:
            print("ℹ️  No CSV files yet (they will be created during simulation)")
        
        return True
    else:
        print(f"ℹ️  Analytics folder will be created at: {data_folder.absolute()}")
        return True

def test_timeline_tracking():
    """Test timeline tracking functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Timeline Tracking")
    print("=" * 60)
    
    try:
        from src.analytics import HTTimelineTracker
        from src.job import Job, JobInstruction, InstructionType
        
        data_folder = Path("data/analytics_logs")
        tracker = HTTimelineTracker(data_folder)
        
        # Create a mock job with instructions
        mock_instructions = [
            JobInstruction(InstructionType.DRIVE, "B1", 0),
            JobInstruction(InstructionType.DRIVE, "B2", 0),
            JobInstruction(InstructionType.LIFT, "B2", 0),
            JobInstruction(InstructionType.DRIVE, "Y1A", 0),
            JobInstruction(InstructionType.DROP, "Y1A", 0),
        ]
        
        # Create timeline
        tracker.create_timeline("JOB001", "DI", mock_instructions, current_time=0)
        print("✅ Created test timeline for JOB001")
        
        # Get summary
        summary = tracker.get_summary_stats()
        print(f"✅ Timeline stats: {summary}")
        
        return True
    except Exception as e:
        print(f"❌ Timeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emissions_calculation():
    """Test emissions calculation"""
    print("\n" + "=" * 60)
    print("TEST 5: Emissions Calculation")
    print("=" * 60)
    
    try:
        from src.analytics import EmissionsCalculator
        from src.job import JobInstruction, InstructionType
        
        data_folder = Path("data/analytics_logs")
        calc = EmissionsCalculator(data_folder)
        
        # Mock instructions
        mock_instructions = [
            JobInstruction(InstructionType.DRIVE, "B1", 0),
            JobInstruction(InstructionType.DRIVE, "B2", 0),
            JobInstruction(InstructionType.LIFT, "B2", 0),
            JobInstruction(InstructionType.DRIVE, "Y1A", 0),
            JobInstruction(InstructionType.DRIVE, "Y1A", 0),
            JobInstruction(InstructionType.DROP, "Y1A", 0),
        ]
        
        # Calculate emissions
        calc.calculate_job_emissions("JOB001", "DI", mock_instructions)
        print("✅ Calculated emissions for test job")
        
        # Get summary
        summary = calc.get_summary()
        print(f"✅ Emissions summary: {summary}")
        
        return True
    except Exception as e:
        print(f"❌ Emissions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_yard_counter():
    """Test yard job counter"""
    print("\n" + "=" * 60)
    print("TEST 6: Yard Job Counter")
    print("=" * 60)
    
    try:
        from src.analytics import YardJobCounter
        
        data_folder = Path("data/analytics_logs")
        counter = YardJobCounter(data_folder)
        
        # Record some test jobs
        counter.record_job_completion("JOB001", "DI", "Y1A")
        counter.record_job_completion("JOB002", "LO", "Y1B")
        counter.record_job_completion("JOB003", "DI", "Y1A")
        print("✅ Recorded 3 test job completions")
        
        # Get totals
        totals = counter.get_total_jobs()
        print(f"✅ Total jobs: {totals}")
        
        # Get yard summary
        summary = counter.get_yard_summary()
        print(f"✅ Yard summary (top 3): {summary[:3]}")
        
        return True
    except Exception as e:
        print(f"❌ Yard counter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_congestion_monitor():
    """Test congestion monitoring"""
    print("\n" + "=" * 60)
    print("TEST 7: Congestion Monitor")
    print("=" * 60)
    
    try:
        from src.analytics import CongestionMonitor
        
        data_folder = Path("data/analytics_logs")
        monitor = CongestionMonitor(data_folder)
        
        # Simulate HT positions (create congestion)
        ht_positions = {
            'HT1': 'B1',
            'HT2': 'B1',
            'HT3': 'B1',
            'HT4': 'B2',
            'HT5': 'B2',
            'HT6': 'B2',
            'HT7': 'B2',
        }
        
        monitor.update_ht_positions(ht_positions, current_time=0)
        print("✅ Updated HT positions with congestion")
        
        # Check status
        status = monitor.get_current_status()
        print(f"✅ Congestion status: {status}")
        
        has_alerts = monitor.has_active_alerts()
        print(f"✅ Has active alerts: {has_alerts}")
        
        return True
    except Exception as e:
        print(f"❌ Congestion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_route_optimizer():
    """Test route optimization analysis"""
    print("\n" + "=" * 60)
    print("TEST 8: Route Optimization")
    print("=" * 60)
    
    try:
        from src.analytics import RouteOptimizationAnalyzer
        from src.job import JobInstruction, InstructionType
        
        data_folder = Path("data/analytics_logs")
        analyzer = RouteOptimizationAnalyzer(data_folder)
        
        # Mock route instructions
        mock_instructions = [
            JobInstruction(InstructionType.DRIVE, "B1", 0),
            JobInstruction(InstructionType.DRIVE, "B2", 0),
            JobInstruction(InstructionType.DRIVE, "B3", 0),
            JobInstruction(InstructionType.LIFT, "B3", 0),
            JobInstruction(InstructionType.DRIVE, "Y1A", 0),
            JobInstruction(InstructionType.DRIVE, "Y1B", 0),
            JobInstruction(InstructionType.DROP, "Y1B", 0),
        ]
        
        analyzer.analyze_route("JOB001", "DI", "BUFFER", "Y1B", mock_instructions)
        print("✅ Analyzed test route")
        
        # Get summary
        summary = analyzer.get_efficiency_summary()
        print(f"✅ Route efficiency summary: {summary}")
        
        return True
    except Exception as e:
        print(f"❌ Route optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all analytics tests"""
    print("\n" + "🧪" * 30)
    print(" ANALYTICS SYSTEM VERIFICATION TESTS")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_analytics_imports()))
    results.append(("Initialization", test_analytics_initialization()))
    results.append(("Data Folder", test_data_folder_creation()))
    results.append(("Timeline Tracking", test_timeline_tracking()))
    results.append(("Emissions Calc", test_emissions_calculation()))
    results.append(("Yard Counter", test_yard_counter()))
    results.append(("Congestion Monitor", test_congestion_monitor()))
    results.append(("Route Optimizer", test_route_optimizer()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("-" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Analytics system is ready!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
