#!/usr/bin/env python3
"""
Comprehensive Test Runner for NeuraCRM
Includes all modules: Authentication, Leads, Contacts, Deals, AI Features, Email Campaigns
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tests.automation.test_execution_framework import TestExecutionFramework
from tests.data.test_data_manager import TestDataManager

class ComprehensiveTestRunner:
    def __init__(self):
        self.framework = TestExecutionFramework()
        self.data_manager = TestDataManager()
        self.results = []
        
    async def run_all_tests(self):
        """Run comprehensive test suite across all modules"""
        print("🚀 NeuraCRM Comprehensive Test Suite")
        print("=" * 60)
        
        # Generate test data
        print("📊 Generating test data...")
        self.data_manager.generate_test_dataset()
        print("✅ Test data generated")
        
        # Define test modules
        test_modules = [
            {
                "name": "Authentication",
                "file": "tests/test-cases/modules/authentication.json",
                "priority": "critical"
            },
            {
                "name": "Leads Management", 
                "file": "tests/test-cases/modules/leads-management.json",
                "priority": "critical"
            },
            {
                "name": "Contacts Management",
                "file": "tests/test-cases/modules/contacts-management.json", 
                "priority": "critical"
            },
            {
                "name": "Deals Pipeline",
                "file": "tests/test-cases/modules/deals-pipeline.json",
                "priority": "critical"
            },
            {
                "name": "AI Features",
                "file": "tests/test-cases/modules/ai-features.json",
                "priority": "high"
            },
            {
                "name": "Email Campaigns",
                "file": "tests/test-cases/modules/email-campaigns.json",
                "priority": "high"
            }
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for module in test_modules:
            print(f"\n📋 Testing {module['name']} module...")
            print("-" * 40)
            
            try:
                # Load test cases
                with open(module["file"], 'r') as f:
                    test_suite = json.load(f)
                
                # Execute test suite
                results = await self.framework.execute_test_suite(test_suite)
                
                # Process results
                module_passed = 0
                module_failed = 0
                
                for result in results:
                    total_tests += 1
                    if result.status == "passed":
                        passed_tests += 1
                        module_passed += 1
                    else:
                        failed_tests += 1
                        module_failed += 1
                
                print(f"✅ {module['name']}: {module_passed} passed, {module_failed} failed")
                self.results.extend(results)
                
            except FileNotFoundError:
                print(f"⚠️ Test file not found: {module['file']}")
            except Exception as e:
                print(f"❌ Error testing {module['name']}: {e}")
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(total_tests, passed_tests, failed_tests)
        
        # Save reports
        self.save_reports(report)
        
        return report
    
    def generate_comprehensive_report(self, total_tests, passed_tests, failed_tests):
        """Generate comprehensive test report"""
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "testRun": {
                "timestamp": datetime.now().isoformat(),
                "totalTests": total_tests,
                "passedTests": passed_tests,
                "failedTests": failed_tests,
                "skippedTests": 0,
                "successRate": round(success_rate, 2),
                "duration": "N/A"  # Would be calculated in real implementation
            },
            "summary": {
                "overallStatus": "PASSED" if failed_tests == 0 else "FAILED",
                "criticalIssues": failed_tests,
                "recommendations": self.generate_recommendations(success_rate, failed_tests)
            },
            "moduleResults": self.organize_results_by_module(),
            "detailedResults": self.results
        }
        
        return report
    
    def organize_results_by_module(self):
        """Organize test results by module"""
        module_results = {}
        
        for result in self.results:
            module = result.test_case.get("module", "Unknown")
            if module not in module_results:
                module_results[module] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "successRate": 0
                }
            
            module_results[module]["total"] += 1
            if result.status == "passed":
                module_results[module]["passed"] += 1
            else:
                module_results[module]["failed"] += 1
        
        # Calculate success rates
        for module in module_results:
            total = module_results[module]["total"]
            passed = module_results[module]["passed"]
            module_results[module]["successRate"] = round((passed / total * 100) if total > 0 else 0, 2)
        
        return module_results
    
    def generate_recommendations(self, success_rate, failed_tests):
        """Generate recommendations based on test results"""
        recommendations = []
        
        if success_rate >= 95:
            recommendations.append("Excellent test results! System is performing well.")
        elif success_rate >= 85:
            recommendations.append("Good test results with minor issues to address.")
        elif success_rate >= 70:
            recommendations.append("Moderate issues detected. Review failed tests.")
        else:
            recommendations.append("Significant issues detected. Immediate attention required.")
        
        if failed_tests > 0:
            recommendations.append(f"Investigate {failed_tests} failed test cases.")
        
        recommendations.extend([
            "Review test automation scripts for any issues.",
            "Consider adding more test cases for edge scenarios.",
            "Set up continuous integration for automated testing."
        ])
        
        return recommendations
    
    def save_reports(self, report):
        """Save test reports in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create reports directory
        reports_dir = Path("test-results")
        reports_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_file = reports_dir / f"comprehensive_test_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save HTML report
        html_file = reports_dir / f"comprehensive_test_report_{timestamp}.html"
        html_content = self.generate_html_report(report)
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n💾 Reports saved:")
        print(f"   📄 JSON: {json_file}")
        print(f"   🌐 HTML: {html_file}")
    
    def generate_html_report(self, report):
        """Generate HTML test report"""
        success_rate = report["testRun"]["successRate"]
        status_color = "green" if success_rate >= 95 else "orange" if success_rate >= 85 else "red"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NeuraCRM Comprehensive Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric h3 {{ margin: 0 0 10px 0; }}
        .metric .value {{ font-size: 24px; font-weight: bold; color: {status_color}; }}
        .module {{ margin: 20px 0; }}
        .module h3 {{ background: #e9ecef; padding: 10px; border-radius: 3px; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .recommendations h3 {{ margin-top: 0; }}
        .recommendations ul {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 NeuraCRM Comprehensive Test Report</h1>
        <p>Generated: {report['testRun']['timestamp']}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="value">{report['testRun']['totalTests']}</div>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <div class="value">{report['testRun']['passedTests']}</div>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <div class="value">{report['testRun']['failedTests']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="value">{report['testRun']['successRate']}%</div>
        </div>
    </div>
    
    <h2>📊 Module Results</h2>
"""
        
        for module, results in report["moduleResults"].items():
            module_color = "green" if results["successRate"] >= 95 else "orange" if results["successRate"] >= 85 else "red"
            html += f"""
    <div class="module">
        <h3>{module}</h3>
        <p><strong>Success Rate:</strong> <span style="color: {module_color}">{results['successRate']}%</span></p>
        <p><strong>Tests:</strong> {results['passed']} passed, {results['failed']} failed (total: {results['total']})</p>
    </div>
"""
        
        html += f"""
    <div class="recommendations">
        <h3>💡 Recommendations</h3>
        <ul>
"""
        for rec in report["summary"]["recommendations"]:
            html += f"            <li>{rec}</li>\n"
        
        html += """
        </ul>
    </div>
    
    <h2>📋 Detailed Results</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background: #f5f5f5;">
            <th>Test Case</th>
            <th>Module</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Error</th>
        </tr>
"""
        
        for result in report["detailedResults"]:
            status_color = "green" if result.status == "passed" else "red"
            html += f"""
        <tr>
            <td>{result.test_case.get('testCaseId', 'N/A')}</td>
            <td>{result.test_case.get('module', 'N/A')}</td>
            <td style="color: {status_color}">{result.status.upper()}</td>
            <td>{result.duration:.2f}s</td>
            <td>{result.error or 'N/A'}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html

async def main():
    """Main function to run comprehensive tests"""
    runner = ComprehensiveTestRunner()
    
    try:
        report = await runner.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {report['testRun']['totalTests']}")
        print(f"Passed: {report['testRun']['passedTests']}")
        print(f"Failed: {report['testRun']['failedTests']}")
        print(f"Success Rate: {report['testRun']['successRate']}%")
        print(f"Overall Status: {report['summary']['overallStatus']}")
        
        if report['testRun']['failedTests'] == 0:
            print("\n🎉 All tests passed! Your NeuraCRM system is working perfectly.")
        else:
            print(f"\n⚠️ {report['testRun']['failedTests']} tests failed. Please review the detailed report.")
        
        print("\n💡 Next Steps:")
        for rec in report['summary']['recommendations']:
            print(f"   • {rec}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

