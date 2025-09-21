#!/usr/bin/env python3
"""
Comprehensive Deals Testing Suite
Runs all deals-related tests including CRUD, Kanban board, and creation scenarios
"""

import subprocess
import sys
import time

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, 
            f"tests/automation/scripts/{script_name}"
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ Test timed out: {script_name}")
        return False
    except Exception as e:
        print(f"❌ Error running test {script_name}: {e}")
        return False

def main():
    """Run comprehensive deals testing suite"""
    print("🚀 NeuraCRM Comprehensive Deals Testing Suite")
    print("=" * 60)
    print("This suite will test all aspects of deals management:")
    print("• CRUD Operations (Create, Read, Update, Delete)")
    print("• Kanban Board Functionality")
    print("• Deal Creation Scenarios")
    print("• Stage Movement and Analytics")
    print("=" * 60)
    
    # Test results tracking
    test_results = []
    
    # Test 1: Deals CRUD Operations
    success = run_test_script(
        "test_deals_crud_complete.py",
        "Deals CRUD Operations Test"
    )
    test_results.append(("Deals CRUD Operations", success))
    
    # Test 2: Kanban Board Functionality
    success = run_test_script(
        "test_deals_kanban_board.py",
        "Deals Kanban Board Test"
    )
    test_results.append(("Kanban Board Functionality", success))
    
    # Test 3: Deal Creation Scenarios
    success = run_test_script(
        "test_deals_create.py",
        "Deals Creation Scenarios Test"
    )
    test_results.append(("Deal Creation Scenarios", success))
    
    # Summary Report
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE DEALS TESTING SUMMARY")
    print(f"{'='*60}")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
        if success:
            passed_tests += 1
    
    print(f"\n📈 RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL DEALS TESTS PASSED!")
        print("   NeuraCRM deals management is fully functional.")
        print("   All CRUD operations, Kanban board, and creation scenarios work correctly.")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed.")
        print("   Please review the failed tests above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

