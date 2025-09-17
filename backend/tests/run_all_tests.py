"""
Master Test Runner
Runs all AI integration tests in sequence and generates comprehensive reports
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import Base
from tests.ai_integration_test import AIIntegrationTestSuite
from tests.api_endpoint_test import APIEndpointTestSuite
from tests.real_world_scenarios_test import RealWorldScenarioTestSuite
from tests.performance_test import PerformanceTestSuite

class MasterTestRunner:
    """Master test runner for all AI integration tests"""
    
    def __init__(self):
        self.all_results = {}
        self.setup_database()
    
    def setup_database(self):
        """Setup test database"""
        # Create test database
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        # Create session
        SessionLocal = sessionmaker(bind=self.engine)
        self.db = SessionLocal()
        
        print("✅ Test database setup complete")
    
    async def run_all_test_suites(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE AI INTEGRATION TEST SUITE")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Test Suite 1: Core AI Integration Tests
        print("\n📋 TEST SUITE 1: Core AI Integration Tests")
        print("-" * 50)
        try:
            core_tests = AIIntegrationTestSuite()
            await core_tests.run_all_tests()
            self.all_results["core_integration"] = core_tests.test_results
        except Exception as e:
            print(f"❌ Core integration tests failed: {str(e)}")
            self.all_results["core_integration"] = {"error": str(e)}
        
        # Test Suite 2: API Endpoint Tests
        print("\n📋 TEST SUITE 2: API Endpoint Tests")
        print("-" * 50)
        try:
            api_tests = APIEndpointTestSuite()
            await api_tests.run_all_tests()
            self.all_results["api_endpoints"] = api_tests.test_results
        except Exception as e:
            print(f"❌ API endpoint tests failed: {str(e)}")
            self.all_results["api_endpoints"] = {"error": str(e)}
        
        # Test Suite 3: Real-World Scenario Tests
        print("\n📋 TEST SUITE 3: Real-World Scenario Tests")
        print("-" * 50)
        try:
            scenario_tests = RealWorldScenarioTestSuite(self.db)
            await scenario_tests.run_all_scenarios()
            self.all_results["real_world_scenarios"] = scenario_tests.test_results
        except Exception as e:
            print(f"❌ Real-world scenario tests failed: {str(e)}")
            self.all_results["real_world_scenarios"] = {"error": str(e)}
        
        # Test Suite 4: Performance Tests
        print("\n📋 TEST SUITE 4: Performance and Load Tests")
        print("-" * 50)
        try:
            performance_tests = PerformanceTestSuite(self.db)
            await performance_tests.run_all_performance_tests()
            self.all_results["performance"] = performance_tests.test_results
        except Exception as e:
            print(f"❌ Performance tests failed: {str(e)}")
            self.all_results["performance"] = {"error": str(e)}
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE AI INTEGRATION TEST REPORT")
        print("="*80)
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        suite_summaries = {}
        
        for suite_name, suite_results in self.all_results.items():
            if isinstance(suite_results, dict) and "error" not in suite_results:
                suite_total = len(suite_results)
                suite_passed = len([r for r in suite_results.values() if isinstance(r, str) and r.startswith("✅")])
                suite_failed = suite_total - suite_passed
                
                total_tests += suite_total
                total_passed += suite_passed
                total_failed += suite_failed
                
                suite_summaries[suite_name] = {
                    "total": suite_total,
                    "passed": suite_passed,
                    "failed": suite_failed,
                    "success_rate": (suite_passed / suite_total * 100) if suite_total > 0 else 0
                }
            else:
                suite_summaries[suite_name] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 1,
                    "success_rate": 0,
                    "error": suite_results.get("error", "Unknown error")
                }
                total_failed += 1
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL SUMMARY:")
        print(f"  Total Test Suites: {len(self.all_results)}")
        print(f"  Total Tests: {total_tests}")
        print(f"  Total Passed: {total_passed}")
        print(f"  Total Failed: {total_failed}")
        print(f"  Overall Success Rate: {overall_success_rate:.1f}%")
        
        print(f"\n📋 TEST SUITE BREAKDOWN:")
        for suite_name, summary in suite_summaries.items():
            if "error" in summary:
                print(f"  {suite_name}: ❌ ERROR - {summary['error']}")
            else:
                status = "✅ PASS" if summary["failed"] == 0 else f"⚠️  {summary['failed']} FAILED"
                print(f"  {suite_name}: {status} ({summary['success_rate']:.1f}% - {summary['passed']}/{summary['total']})")
        
        # Detailed results by suite
        print(f"\n📋 DETAILED RESULTS BY SUITE:")
        for suite_name, suite_results in self.all_results.items():
            print(f"\n  🔍 {suite_name.upper().replace('_', ' ')}:")
            if isinstance(suite_results, dict) and "error" not in suite_results:
                for test_name, result in suite_results.items():
                    if isinstance(result, dict):
                        print(f"    {test_name}:")
                        for key, value in result.items():
                            print(f"      {key}: {value}")
                    else:
                        print(f"    {test_name}: {result}")
            else:
                print(f"    ERROR: {suite_results.get('error', 'Unknown error')}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if overall_success_rate >= 90:
            print("  🎉 EXCELLENT! AI integration is working very well.")
            print("  ✅ Ready for production deployment.")
        elif overall_success_rate >= 75:
            print("  ✅ GOOD! AI integration is mostly working well.")
            print("  ⚠️  Address failed tests before production deployment.")
        elif overall_success_rate >= 50:
            print("  ⚠️  MODERATE! AI integration has significant issues.")
            print("  🔧 Major fixes needed before production deployment.")
        else:
            print("  ❌ POOR! AI integration has major problems.")
            print("  🚨 Extensive debugging and fixes required.")
        
        # Specific recommendations based on test results
        if "core_integration" in self.all_results:
            core_results = self.all_results["core_integration"]
            if isinstance(core_results, dict):
                failed_core = [k for k, v in core_results.items() if isinstance(v, str) and v.startswith("❌")]
                if failed_core:
                    print(f"  🔧 Fix core integration issues: {', '.join(failed_core)}")
        
        if "api_endpoints" in self.all_results:
            api_results = self.all_results["api_endpoints"]
            if isinstance(api_results, dict):
                failed_api = [k for k, v in api_results.items() if isinstance(v, str) and v.startswith("❌")]
                if failed_api:
                    print(f"  🔧 Fix API endpoint issues: {', '.join(failed_api)}")
        
        if "performance" in self.all_results:
            perf_results = self.all_results["performance"]
            if isinstance(perf_results, dict) and "response_times" in perf_results:
                response_times = perf_results["response_times"]
                if isinstance(response_times, dict) and "average" in response_times:
                    avg_time = float(response_times["average"].replace("s", ""))
                    if avg_time > 5.0:
                        print("  ⚡ Optimize response times (currently >5s average)")
                    elif avg_time < 2.0:
                        print("  ✅ Response times are excellent")
        
        print("\n" + "="*80)
        
        # Save comprehensive report
        comprehensive_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_summary": {
                "total_suites": len(self.all_results),
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "overall_success_rate": overall_success_rate
            },
            "suite_summaries": suite_summaries,
            "detailed_results": self.all_results
        }
        
        with open("comprehensive_ai_test_report.json", "w") as f:
            json.dump(comprehensive_report, f, indent=2)
        
        print("📄 Comprehensive test report saved to: comprehensive_ai_test_report.json")
        
        # Return success/failure status
        return overall_success_rate >= 75

async def main():
    """Main test runner function"""
    runner = MasterTestRunner()
    success = await runner.run_all_test_suites()
    
    if success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
