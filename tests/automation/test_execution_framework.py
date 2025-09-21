#!/usr/bin/env python3
"""
NeuraCRM Test Execution Framework
Comprehensive test execution system for regression testing
"""

import json
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import subprocess
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@dataclass
class TestResult:
    """Test execution result"""
    test_case_id: str
    title: str
    status: str  # passed, failed, skipped, error
    execution_time: float
    error_message: Optional[str] = None
    screenshots: List[str] = None
    logs: List[str] = None
    timestamp: str = None

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    module: str
    test_cases: List[Dict[str, Any]]
    execution_order: str = "sequential"  # sequential, parallel, priority
    timeout: int = 300  # 5 minutes default

class TestExecutionFramework:
    """Main test execution framework"""
    
    def __init__(self, config_path: str = "tests/config/test_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.results: List[TestResult] = []
        self.logger = self.setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default test configuration"""
        return {
            "test_environment": {
                "base_url": "http://localhost:5173",
                "api_url": "http://localhost:8000",
                "browser": "chromium",
                "headless": False,
                "timeout": 30000
            },
            "test_data": {
                "test_user": {
                    "email": "nodeit@node.com",
                    "password": "NodeIT2024!"
                }
            },
            "reporting": {
                "output_dir": "test-results",
                "generate_html": True,
                "generate_json": True,
                "generate_junit": True
            },
            "execution": {
                "parallel_workers": 2,
                "retry_failed": True,
                "max_retries": 2,
                "stop_on_failure": False
            }
        }
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('test_execution')
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs('test-results/logs', exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(
            f'test-results/logs/test_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def load_test_cases(self, module: str) -> List[Dict[str, Any]]:
        """Load test cases for a specific module"""
        test_file = f"tests/test-cases/modules/{module}.json"
        try:
            with open(test_file, 'r') as f:
                data = json.load(f)
                return data.get('testCases', [])
        except FileNotFoundError:
            self.logger.error(f"Test cases file not found: {test_file}")
            return []
    
    def create_test_suite(self, module: str, test_cases: List[Dict[str, Any]]) -> TestSuite:
        """Create a test suite from test cases"""
        return TestSuite(
            name=f"{module}_test_suite",
            module=module,
            test_cases=test_cases
        )
    
    async def execute_test_case(self, test_case: Dict[str, Any]) -> TestResult:
        """Execute a single test case"""
        test_id = test_case.get('testCaseId', 'unknown')
        title = test_case.get('title', 'Untitled Test')
        
        self.logger.info(f"Executing test case: {test_id} - {title}")
        
        start_time = time.time()
        
        try:
            # Check if test is automated
            automation = test_case.get('automation', {})
            if automation.get('automated', False):
                result = await self.execute_automated_test(test_case)
            else:
                result = await self.execute_manual_test(test_case)
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_case_id=test_id,
                title=title,
                status=result['status'],
                execution_time=execution_time,
                error_message=result.get('error_message'),
                screenshots=result.get('screenshots', []),
                logs=result.get('logs', []),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Test case {test_id} failed with exception: {str(e)}")
            
            return TestResult(
                test_case_id=test_id,
                title=title,
                status='error',
                execution_time=execution_time,
                error_message=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    async def execute_automated_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated test using Playwright"""
        automation = test_case.get('automation', {})
        script = automation.get('script')
        
        if not script:
            return {
                'status': 'skipped',
                'error_message': 'No automation script specified'
            }
        
        try:
            # Run Playwright test
            script_path = f"tests/automation/scripts/{script}"
            if not os.path.exists(script_path):
                return {
                    'status': 'error',
                    'error_message': f'Automation script not found: {script_path}'
                }
            
            # Execute the test script
            result = subprocess.run([
                'npx', 'playwright', 'test', script_path,
                '--config=tests/regression.config.ts'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'logs': [result.stdout]
                }
            else:
                return {
                    'status': 'failed',
                    'error_message': result.stderr,
                    'logs': [result.stdout, result.stderr]
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'error_message': 'Test execution timeout'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    async def execute_manual_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Execute manual test (placeholder for manual execution)"""
        # For manual tests, we create a test execution guide
        test_guide = self.generate_manual_test_guide(test_case)
        
        # In a real implementation, this would integrate with a manual test management system
        # For now, we'll mark it as pending manual execution
        return {
            'status': 'pending_manual',
            'logs': [test_guide]
        }
    
    def generate_manual_test_guide(self, test_case: Dict[str, Any]) -> str:
        """Generate manual test execution guide"""
        guide = f"""
MANUAL TEST EXECUTION GUIDE
==========================

Test Case ID: {test_case.get('testCaseId', 'N/A')}
Title: {test_case.get('title', 'N/A')}
Module: {test_case.get('module', 'N/A')}
Priority: {test_case.get('priority', 'N/A')}
Type: {test_case.get('type', 'N/A')}

Description:
{test_case.get('description', 'N/A')}

Prerequisites:
{chr(10).join(f"- {p}" for p in test_case.get('prerequisites', []))}

Test Steps:
"""
        
        for step in test_case.get('testSteps', []):
            guide += f"""
Step {step.get('step', 'N/A')}:
Action: {step.get('action', 'N/A')}
Expected Result: {step.get('expectedResult', 'N/A')}
"""
        
        guide += f"""
Test Data:
{json.dumps(test_case.get('testData', {}), indent=2)}

Expected Results:
{chr(10).join(f"- {r}" for r in test_case.get('expectedResults', []))}

Estimated Time: {test_case.get('estimatedTime', 'N/A')}
"""
        
        return guide
    
    async def execute_test_suite(self, test_suite: TestSuite) -> List[TestResult]:
        """Execute a complete test suite"""
        self.logger.info(f"Executing test suite: {test_suite.name}")
        
        results = []
        
        for test_case in test_suite.test_cases:
            result = await self.execute_test_case(test_case)
            results.append(result)
            self.results.append(result)
            
            # Log result
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'error': '💥',
                'pending_manual': '👤'
            }.get(result.status, '❓')
            
            self.logger.info(
                f"{status_emoji} {result.test_case_id}: {result.title} "
                f"({result.execution_time:.2f}s)"
            )
            
            if result.error_message:
                self.logger.error(f"Error: {result.error_message}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == 'passed'])
        failed_tests = len([r for r in self.results if r.status == 'failed'])
        error_tests = len([r for r in self.results if r.status == 'error'])
        skipped_tests = len([r for r in self.results if r.status == 'skipped'])
        manual_tests = len([r for r in self.results if r.status == 'pending_manual'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_execution_time = sum(r.execution_time for r in self.results)
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'error': error_tests,
                'skipped': skipped_tests,
                'manual_pending': manual_tests,
                'success_rate': round(success_rate, 2),
                'total_execution_time': round(total_execution_time, 2),
                'timestamp': datetime.now().isoformat()
            },
            'results': [
                {
                    'test_case_id': r.test_case_id,
                    'title': r.title,
                    'status': r.status,
                    'execution_time': r.execution_time,
                    'error_message': r.error_message,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ],
            'failed_tests': [
                {
                    'test_case_id': r.test_case_id,
                    'title': r.title,
                    'error_message': r.error_message
                }
                for r in self.results if r.status in ['failed', 'error']
            ]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], format: str = 'json') -> str:
        """Save test report in specified format"""
        os.makedirs('test-results', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f'test-results/test_report_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
        
        elif format == 'html':
            filename = f'test-results/test_report_{timestamp}.html'
            html_content = self.generate_html_report(report)
            with open(filename, 'w') as f:
                f.write(html_content)
        
        return filename
    
    def generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML test report"""
        summary = report['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NeuraCRM Test Report - {summary['timestamp']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric .value {{ font-size: 24px; font-weight: bold; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .error {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .manual {{ color: #17a2b8; }}
        .results {{ margin-top: 30px; }}
        .test-result {{ padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .test-result.passed {{ background: #d4edda; }}
        .test-result.failed {{ background: #f8d7da; }}
        .test-result.error {{ background: #f8d7da; }}
        .test-result.skipped {{ background: #fff3cd; }}
        .test-result.manual {{ background: #d1ecf1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 NeuraCRM Test Execution Report</h1>
        <p>Generated on: {summary['timestamp']}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="value">{summary['total_tests']}</div>
        </div>
        <div class="metric">
            <h3>Passed</h3>
            <div class="value passed">{summary['passed']}</div>
        </div>
        <div class="metric">
            <h3>Failed</h3>
            <div class="value failed">{summary['failed']}</div>
        </div>
        <div class="metric">
            <h3>Errors</h3>
            <div class="value error">{summary['error']}</div>
        </div>
        <div class="metric">
            <h3>Skipped</h3>
            <div class="value skipped">{summary['skipped']}</div>
        </div>
        <div class="metric">
            <h3>Manual Pending</h3>
            <div class="value manual">{summary['manual_pending']}</div>
        </div>
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="value">{summary['success_rate']}%</div>
        </div>
        <div class="metric">
            <h3>Total Time</h3>
            <div class="value">{summary['total_execution_time']}s</div>
        </div>
    </div>
    
    <div class="results">
        <h2>Test Results</h2>
"""
        
        for result in report['results']:
            status_class = result['status']
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'error': '💥',
                'pending_manual': '👤'
            }.get(result['status'], '❓')
            
            html += f"""
        <div class="test-result {status_class}">
            <strong>{status_emoji} {result['test_case_id']}</strong>: {result['title']}
            <br>
            <small>Status: {result['status']} | Time: {result['execution_time']:.2f}s</small>
"""
            
            if result['error_message']:
                html += f"<br><small style='color: #dc3545;'>Error: {result['error_message']}</small>"
            
            html += "</div>"
        
        html += """
    </div>
</body>
</html>
"""
        
        return html

async def main():
    """Main execution function"""
    framework = TestExecutionFramework()
    
    # Load and execute test cases for each module
    modules = ['authentication', 'leads-management', 'contacts-management', 'deals-pipeline']
    
    for module in modules:
        test_cases = framework.load_test_cases(module)
        if test_cases:
            test_suite = framework.create_test_suite(module, test_cases)
            await framework.execute_test_suite(test_suite)
    
    # Generate and save reports
    report = framework.generate_report()
    
    # Save JSON report
    json_file = framework.save_report(report, 'json')
    print(f"JSON report saved: {json_file}")
    
    # Save HTML report
    html_file = framework.save_report(report, 'html')
    print(f"HTML report saved: {html_file}")
    
    # Print summary
    summary = report['summary']
    print(f"\n📊 TEST EXECUTION SUMMARY")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✅")
    print(f"Failed: {summary['failed']} ❌")
    print(f"Errors: {summary['error']} 💥")
    print(f"Skipped: {summary['skipped']} ⏭️")
    print(f"Manual Pending: {summary['manual_pending']} 👤")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Total Time: {summary['total_execution_time']}s")

if __name__ == "__main__":
    asyncio.run(main())

