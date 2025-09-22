#!/usr/bin/env python3
"""
Comprehensive Test Runner for Automation Features
Tests Lead Assignment Rules and Task Automation functionality
"""

import subprocess
import sys
import time
from datetime import datetime

def run_test_script(script_path, test_name):
    """Run a test script and return the result"""
    print(f"\n{'='*60}")
    print(f"🎯 {test_name}")
    print(f"{'='*60}")
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            print(f"✅ {test_name} - PASSED (Duration: {duration:.2f}s)")
            return True
        else:
            print(f"❌ {test_name} - FAILED (Duration: {duration:.2f}s)")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} - TIMEOUT (Duration: 300s)")
        return False
    except Exception as e:
        print(f"💥 {test_name} - ERROR: {e}")
        return False

def main():
    """Run all automation feature tests"""
    print("🤖 COMPREHENSIVE AUTOMATION FEATURES TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test scripts to run
    test_scripts = [
        {
            "path": "tests/automation/scripts/test_lead_assignment_rules_page_load.py",
            "name": "Lead Assignment Rules Page Load Test"
        },
        {
            "path": "tests/automation/scripts/test_task_automation_page_load.py", 
            "name": "Task Automation Page Load Test"
        }
    ]
    
    # Run tests
    results = []
    for test in test_scripts:
        success = run_test_script(test["path"], test["name"])
        results.append({
            "name": test["name"],
            "success": success
        })
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 AUTOMATION FEATURES TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"  {status} - {result['name']}")
    
    # Save report
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "results": results
    }
    
    import json
    report_file = f"test-results/automation_features_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n📄 Test report saved: {report_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")
    
    if failed_tests > 0:
        print(f"\n⚠️ {failed_tests} AUTOMATION FEATURES TESTS FAILED")
        sys.exit(1)
    else:
        print(f"\n🎉 ALL AUTOMATION FEATURES TESTS PASSED!")
        sys.exit(0)

if __name__ == "__main__":
    main()
