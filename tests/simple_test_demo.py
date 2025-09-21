#!/usr/bin/env python3
"""
Simple demonstration of the NeuraCRM testing framework
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test basic API endpoints"""
    print("🧪 NeuraCRM API Testing Demo")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    results = []
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            results.append({"test": "health_check", "status": "passed", "response_time": response.elapsed.total_seconds()})
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            results.append({"test": "health_check", "status": "failed", "error": f"Status {response.status_code}"})
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        results.append({"test": "health_check", "status": "error", "error": str(e)})
    
    # Test 2: Login
    print("2. Testing login endpoint...")
    try:
        login_data = {
            "email": "nodeit@node.com",
            "password": "NodeIT2024!"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print("   ✅ Login successful")
                results.append({"test": "login", "status": "passed", "response_time": response.elapsed.total_seconds()})
                token = data['access_token']
            else:
                print("   ⚠️ Login successful but no token")
                results.append({"test": "login", "status": "warning", "error": "No access token"})
                token = None
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            results.append({"test": "login", "status": "failed", "error": f"Status {response.status_code}"})
            token = None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        results.append({"test": "login", "status": "error", "error": str(e)})
        token = None
    
    # Test 3: Protected endpoint (if we have a token)
    if token:
        print("3. Testing protected endpoint...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/api/leads", headers=headers, timeout=5)
            if response.status_code == 200:
                print("   ✅ Protected endpoint accessible")
                results.append({"test": "protected_endpoint", "status": "passed", "response_time": response.elapsed.total_seconds()})
            else:
                print(f"   ❌ Protected endpoint failed: {response.status_code}")
                results.append({"test": "protected_endpoint", "status": "failed", "error": f"Status {response.status_code}"})
        except Exception as e:
            print(f"   ❌ Protected endpoint error: {e}")
            results.append({"test": "protected_endpoint", "status": "error", "error": str(e)})
    else:
        print("3. Skipping protected endpoint test (no token)")
        results.append({"test": "protected_endpoint", "status": "skipped", "error": "No access token"})
    
    # Test 4: API Test endpoint
    print("4. Testing API test endpoint...")
    try:
        response = requests.get(f"{base_url}/api/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API test endpoint working")
            results.append({"test": "api_test", "status": "passed", "response_time": response.elapsed.total_seconds()})
        else:
            print(f"   ❌ API test endpoint failed: {response.status_code}")
            results.append({"test": "api_test", "status": "failed", "error": f"Status {response.status_code}"})
    except Exception as e:
        print(f"   ❌ API test endpoint error: {e}")
        results.append({"test": "api_test", "status": "error", "error": str(e)})
    
    return results

def generate_report(results):
    """Generate a simple test report"""
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = len([r for r in results if r['status'] == 'passed'])
    failed_tests = len([r for r in results if r['status'] == 'failed'])
    error_tests = len([r for r in results if r['status'] == 'error'])
    skipped_tests = len([r for r in results if r['status'] == 'skipped'])
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Errors: {error_tests}")
    print(f"Skipped: {skipped_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status_icon = {
            'passed': '✅',
            'failed': '❌',
            'error': '💥',
            'skipped': '⏭️',
            'warning': '⚠️'
        }.get(result['status'], '❓')
        
        print(f"  {status_icon} {result['test']}: {result['status']}")
        if 'error' in result:
            print(f"      Error: {result['error']}")
        if 'response_time' in result:
            print(f"      Time: {result['response_time']:.2f}s")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "error": error_tests,
            "skipped": skipped_tests,
            "success_rate": success_rate
        },
        "results": results
    }
    
    import os
    os.makedirs("test-results", exist_ok=True)
    
    with open("test-results/simple_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved: test-results/simple_test_report.json")
    
    return success_rate >= 75

def main():
    """Main function"""
    print("🚀 NeuraCRM Simple Test Demo")
    print("=" * 50)
    print("This demonstrates the testing framework working with your system")
    print("=" * 50)
    
    # Run tests
    results = test_api_endpoints()
    
    # Generate report
    success = generate_report(results)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Demo completed successfully!")
        print("✅ Your NeuraCRM system is working correctly.")
        print("✅ The testing framework is functional.")
    else:
        print("⚠️ Some tests failed.")
        print("🔧 Please check the issues above.")
    
    print("\n💡 Next steps:")
    print("1. Create automation scripts for UI testing")
    print("2. Add more comprehensive test cases")
    print("3. Set up CI/CD integration")
    print("4. Run full regression test suite")

if __name__ == "__main__":
    main()

