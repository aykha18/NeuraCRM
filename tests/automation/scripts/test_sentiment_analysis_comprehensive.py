#!/usr/bin/env python3
"""
Comprehensive Sentiment Analysis Test Suite
Runs all sentiment analysis tests in sequence
"""

import subprocess
import sys
import time
from datetime import datetime

def run_test_script(script_name, description):
    """Run a test script and return the result"""
    print(f"\n{'='*60}")
    print(f"😊 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, 
            f"tests/automation/scripts/{script_name}"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_sentiment_analysis_comprehensive():
    """Run comprehensive sentiment analysis test suite"""
    
    print("😊 COMPREHENSIVE SENTIMENT ANALYSIS TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test scripts to run
    test_scripts = [
        {
            "script": "test_sentiment_analysis_page_load.py",
            "description": "Sentiment Analysis Page Load Test"
        },
        {
            "script": "test_sentiment_analysis_navigation.py", 
            "description": "Sentiment Analysis Navigation Test"
        },
        {
            "script": "test_sentiment_analysis_data_display.py",
            "description": "Sentiment Analysis Data Display Test"
        },
        {
            "script": "test_sentiment_analysis_api_integration.py",
            "description": "Sentiment Analysis API Integration Test"
        }
    ]
    
    # Run all tests
    results = []
    passed = 0
    failed = 0
    
    for test in test_scripts:
        success = run_test_script(test["script"], test["description"])
        results.append({
            "test": test["description"],
            "script": test["script"],
            "passed": success
        })
        
        if success:
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        time.sleep(2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 SENTIMENT ANALYSIS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {len(test_scripts)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_scripts)*100):.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"  {status} - {result['test']}")
    
    # Generate test report
    report_data = {
        "test_suite": "Sentiment Analysis Comprehensive",
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(test_scripts),
        "passed": passed,
        "failed": failed,
        "success_rate": passed/len(test_scripts)*100,
        "results": results
    }
    
    # Save report
    import json
    report_filename = f"test-results/sentiment_analysis_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Test report saved: {report_filename}")
    
    if failed == 0:
        print(f"\n🎉 ALL SENTIMENT ANALYSIS TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} SENTIMENT ANALYSIS TESTS FAILED")
        return False

if __name__ == "__main__":
    success = test_sentiment_analysis_comprehensive()
    sys.exit(0 if success else 1)

