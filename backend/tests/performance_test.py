"""
Performance and Load Testing Suite
Tests AI integration performance, cost optimization, and scalability
"""
import asyncio
import time
import json
import statistics
from datetime import datetime
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai.sales_assistant_optimized import OptimizedSalesAssistant
from ai.providers.openai_provider import OpenAIProvider
from ai.providers.base import AIModel

class PerformanceTestSuite:
    """Performance and load testing suite for AI integration"""
    
    def __init__(self, db_session, user_id: int = 1, organization_id: int = 1):
        self.db = db_session
        self.user_id = user_id
        self.organization_id = organization_id
        self.test_results = {}
        
        # Initialize AI assistant
        self.assistant = OptimizedSalesAssistant(
            db=self.db,
            user_id=self.user_id,
            organization_id=self.organization_id,
            provider=OpenAIProvider(model=AIModel.GPT_4O_MINI)
        )
    
    async def run_all_performance_tests(self):
        """Run all performance tests"""
        print("\n🚀 Starting Performance and Load Tests\n")
        
        # Test 1: Response Time Analysis
        await self.test_response_times()
        
        # Test 2: Concurrent Request Handling
        await self.test_concurrent_requests()
        
        # Test 3: Memory Usage Analysis
        await self.test_memory_usage()
        
        # Test 4: Cost Analysis
        await self.test_cost_analysis()
        
        # Test 5: Function Call Performance
        await self.test_function_call_performance()
        
        # Test 6: Data Access Performance
        await self.test_data_access_performance()
        
        # Test 7: Error Recovery Performance
        await self.test_error_recovery_performance()
        
        # Test 8: Scalability Testing
        await self.test_scalability()
        
        # Generate performance report
        self.generate_performance_report()
    
    async def test_response_times(self):
        """Test response times for different types of requests"""
        print("🧪 Testing Response Times...")
        
        test_messages = [
            "Hello, how are you?",
            "Analyze my pipeline and suggest improvements",
            "Generate an email for lead #1 using template #1",
            "Search for all contacts with 'ACME' in their name",
            "What are my top 5 deals by value?",
            "Create a follow-up schedule for deal #1",
            "Analyze the competitive landscape for my current deals",
            "Provide sales forecasting for the next quarter"
        ]
        
        response_times = []
        
        for i, message in enumerate(test_messages):
            try:
                start_time = time.time()
                result = await self.assistant.process_message(message)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                
                print(f"  📊 Message {i+1}: {response_time:.2f}s - {message[:50]}...")
                
            except Exception as e:
                print(f"  ❌ Message {i+1} failed: {str(e)}")
                response_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in response_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            
            self.test_results["response_times"] = {
                "average": f"{avg_time:.2f}s",
                "median": f"{median_time:.2f}s",
                "min": f"{min_time:.2f}s",
                "max": f"{max_time:.2f}s",
                "total_tests": len(test_messages),
                "successful_tests": len(valid_times)
            }
            
            print(f"  ✅ Average response time: {avg_time:.2f}s")
            print(f"  ✅ Median response time: {median_time:.2f}s")
            print(f"  ✅ Min/Max: {min_time:.2f}s / {max_time:.2f}s")
        else:
            self.test_results["response_times"] = "❌ FAIL: All requests failed"
            print("  ❌ All response time tests failed")
    
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("🧪 Testing Concurrent Request Handling...")
        
        async def make_request(request_id: int):
            """Make a single request"""
            try:
                start_time = time.time()
                result = await self.assistant.process_message(f"Test request {request_id}")
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "success": True,
                    "response_time": end_time - start_time,
                    "response_length": len(result.get("response", ""))
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                    "response_time": None
                }
        
        # Test with different concurrency levels
        concurrency_levels = [1, 3, 5, 10]
        
        for concurrency in concurrency_levels:
            print(f"  📊 Testing {concurrency} concurrent requests...")
            
            start_time = time.time()
            tasks = [make_request(i) for i in range(concurrency)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_time = end_time - start_time
            successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_requests = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            if successful_requests:
                avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
                success_rate = len(successful_requests) / concurrency * 100
                
                self.test_results[f"concurrent_{concurrency}"] = {
                    "total_time": f"{total_time:.2f}s",
                    "avg_response_time": f"{avg_response_time:.2f}s",
                    "success_rate": f"{success_rate:.1f}%",
                    "successful_requests": len(successful_requests),
                    "failed_requests": len(failed_requests)
                }
                
                print(f"    ✅ Success rate: {success_rate:.1f}%")
                print(f"    ✅ Avg response time: {avg_response_time:.2f}s")
                print(f"    ✅ Total time: {total_time:.2f}s")
            else:
                self.test_results[f"concurrent_{concurrency}"] = "❌ FAIL: All requests failed"
                print(f"    ❌ All {concurrency} concurrent requests failed")
    
    async def test_memory_usage(self):
        """Test memory usage patterns"""
        print("🧪 Testing Memory Usage...")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Make multiple requests to test memory growth
            for i in range(10):
                await self.assistant.process_message(f"Memory test request {i}")
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            self.test_results["memory_usage"] = {
                "initial_memory": f"{initial_memory:.2f} MB",
                "final_memory": f"{final_memory:.2f} MB",
                "memory_increase": f"{memory_increase:.2f} MB",
                "memory_per_request": f"{memory_increase/10:.2f} MB"
            }
            
            print(f"  ✅ Initial memory: {initial_memory:.2f} MB")
            print(f"  ✅ Final memory: {final_memory:.2f} MB")
            print(f"  ✅ Memory increase: {memory_increase:.2f} MB")
            print(f"  ✅ Memory per request: {memory_increase/10:.2f} MB")
            
        except ImportError:
            self.test_results["memory_usage"] = "⚠️ SKIP: psutil not available"
            print("  ⚠️ Memory usage test skipped (psutil not available)")
        except Exception as e:
            self.test_results["memory_usage"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Memory usage test failed: {str(e)}")
    
    async def test_cost_analysis(self):
        """Test cost analysis and optimization"""
        print("🧪 Testing Cost Analysis...")
        
        try:
            # Get model cost information
            model_info = self.assistant.provider.get_model_info()
            cost_info = self.assistant.provider._get_cost_info()
            
            # Make a test request and analyze usage
            result = await self.assistant.process_message("Analyze my sales pipeline")
            
            usage = result.get("usage", {})
            if usage:
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                
                # Calculate costs
                input_cost = (prompt_tokens / 1000) * cost_info["input"]
                output_cost = (completion_tokens / 1000) * cost_info["output"]
                total_cost = input_cost + output_cost
                
                self.test_results["cost_analysis"] = {
                    "model": model_info["model"],
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "input_cost": f"${input_cost:.6f}",
                    "output_cost": f"${output_cost:.6f}",
                    "total_cost": f"${total_cost:.6f}",
                    "cost_per_1k_tokens": f"${(total_cost / total_tokens * 1000):.6f}" if total_tokens > 0 else "N/A"
                }
                
                print(f"  ✅ Model: {model_info['model']}")
                print(f"  ✅ Total tokens: {total_tokens}")
                print(f"  ✅ Total cost: ${total_cost:.6f}")
                print(f"  ✅ Cost per 1K tokens: ${(total_cost / total_tokens * 1000):.6f}" if total_tokens > 0 else "N/A")
            else:
                self.test_results["cost_analysis"] = "⚠️ SKIP: Usage data not available"
                print("  ⚠️ Cost analysis skipped (usage data not available)")
                
        except Exception as e:
            self.test_results["cost_analysis"] = f"❌ FAIL: {str(e)}"
            print(f"  ❌ Cost analysis failed: {str(e)}")
    
    async def test_function_call_performance(self):
        """Test function call performance"""
        print("🧪 Testing Function Call Performance...")
        
        function_tests = [
            {"name": "get_lead_details", "args": {"lead_id": 1}},
            {"name": "get_deal_details", "args": {"deal_id": 1}},
            {"name": "search_crm", "args": {"query": "test", "entity_types": ["contacts"]}},
            {"name": "get_email_templates", "args": {"category": "welcome"}},
            {"name": "analyze_pipeline", "args": {}}
        ]
        
        function_times = []
        
        for test in function_tests:
            try:
                start_time = time.time()
                result = await self.assistant._execute_function({
                    "name": test["name"],
                    "arguments": test["args"]
                })
                end_time = time.time()
                
                response_time = end_time - start_time
                function_times.append(response_time)
                
                success = result.get("success", False)
                print(f"  📊 {test['name']}: {response_time:.2f}s - {'✅' if success else '❌'}")
                
            except Exception as e:
                print(f"  ❌ {test['name']} failed: {str(e)}")
                function_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in function_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            
            self.test_results["function_call_performance"] = {
                "average_time": f"{avg_time:.2f}s",
                "median_time": f"{median_time:.2f}s",
                "total_functions": len(function_tests),
                "successful_functions": len(valid_times)
            }
            
            print(f"  ✅ Average function call time: {avg_time:.2f}s")
            print(f"  ✅ Median function call time: {median_time:.2f}s")
        else:
            self.test_results["function_call_performance"] = "❌ FAIL: All function calls failed"
            print("  ❌ All function call tests failed")
    
    async def test_data_access_performance(self):
        """Test data access layer performance"""
        print("🧪 Testing Data Access Performance...")
        
        data_access_tests = [
            {"name": "get_user_context", "func": self.assistant.data_access.get_user_context},
            {"name": "get_organization_context", "func": self.assistant.data_access.get_organization_context},
            {"name": "get_lead_context", "func": lambda: self.assistant.data_access.get_lead_context(1)},
            {"name": "get_deal_context", "func": lambda: self.assistant.data_access.get_deal_context(1)},
            {"name": "get_contact_context", "func": lambda: self.assistant.data_access.get_contact_context(1)},
            {"name": "get_pipeline_summary", "func": self.assistant.data_access.get_pipeline_summary},
            {"name": "search_entities", "func": lambda: self.assistant.data_access.search_entities("test", ["contacts"])}
        ]
        
        data_access_times = []
        
        for test in data_access_tests:
            try:
                start_time = time.time()
                result = test["func"]()
                end_time = time.time()
                
                response_time = end_time - start_time
                data_access_times.append(response_time)
                
                print(f"  📊 {test['name']}: {response_time:.3f}s")
                
            except Exception as e:
                print(f"  ❌ {test['name']} failed: {str(e)}")
                data_access_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in data_access_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            
            self.test_results["data_access_performance"] = {
                "average_time": f"{avg_time:.3f}s",
                "median_time": f"{median_time:.3f}s",
                "total_operations": len(data_access_tests),
                "successful_operations": len(valid_times)
            }
            
            print(f"  ✅ Average data access time: {avg_time:.3f}s")
            print(f"  ✅ Median data access time: {median_time:.3f}s")
        else:
            self.test_results["data_access_performance"] = "❌ FAIL: All data access operations failed"
            print("  ❌ All data access tests failed")
    
    async def test_error_recovery_performance(self):
        """Test error recovery performance"""
        print("🧪 Testing Error Recovery Performance...")
        
        error_tests = [
            {"name": "Invalid Lead ID", "message": "Get details for lead #99999"},
            {"name": "Invalid Deal ID", "message": "Get details for deal #99999"},
            {"name": "Invalid Function", "message": "Call invalid_function with args"},
            {"name": "Malformed Request", "message": "Generate email with invalid template ID"},
            {"name": "Empty Search", "message": "Search for 'nonexistent_company_xyz'"}
        ]
        
        error_recovery_times = []
        successful_recoveries = 0
        
        for test in error_tests:
            try:
                start_time = time.time()
                result = await self.assistant.process_message(test["message"])
                end_time = time.time()
                
                response_time = end_time - start_time
                error_recovery_times.append(response_time)
                
                # Check if the assistant handled the error gracefully
                if result.get("response") and len(result["response"]) > 0:
                    successful_recoveries += 1
                    print(f"  📊 {test['name']}: {response_time:.2f}s - ✅ Recovered")
                else:
                    print(f"  📊 {test['name']}: {response_time:.2f}s - ❌ No response")
                
            except Exception as e:
                print(f"  ❌ {test['name']} failed: {str(e)}")
                error_recovery_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in error_recovery_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            recovery_rate = successful_recoveries / len(error_tests) * 100
            
            self.test_results["error_recovery_performance"] = {
                "average_recovery_time": f"{avg_time:.2f}s",
                "recovery_rate": f"{recovery_rate:.1f}%",
                "successful_recoveries": successful_recoveries,
                "total_error_tests": len(error_tests)
            }
            
            print(f"  ✅ Average error recovery time: {avg_time:.2f}s")
            print(f"  ✅ Error recovery rate: {recovery_rate:.1f}%")
        else:
            self.test_results["error_recovery_performance"] = "❌ FAIL: All error recovery tests failed"
            print("  ❌ All error recovery tests failed")
    
    async def test_scalability(self):
        """Test scalability with increasing load"""
        print("🧪 Testing Scalability...")
        
        # Test with increasing number of requests
        load_levels = [5, 10, 20, 50]
        
        for load in load_levels:
            print(f"  📊 Testing with {load} requests...")
            
            async def make_scalability_request(request_id: int):
                try:
                    start_time = time.time()
                    result = await self.assistant.process_message(f"Scalability test request {request_id}")
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "success": True,
                        "response_time": end_time - start_time
                    }
                except Exception as e:
                    return {
                        "request_id": request_id,
                        "success": False,
                        "error": str(e)
                    }
            
            start_time = time.time()
            tasks = [make_scalability_request(i) for i in range(load)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            total_time = end_time - start_time
            successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
            
            if successful_requests:
                avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
                throughput = len(successful_requests) / total_time  # requests per second
                success_rate = len(successful_requests) / load * 100
                
                self.test_results[f"scalability_{load}"] = {
                    "total_time": f"{total_time:.2f}s",
                    "avg_response_time": f"{avg_response_time:.2f}s",
                    "throughput": f"{throughput:.2f} req/s",
                    "success_rate": f"{success_rate:.1f}%",
                    "successful_requests": len(successful_requests)
                }
                
                print(f"    ✅ Throughput: {throughput:.2f} req/s")
                print(f"    ✅ Success rate: {success_rate:.1f}%")
                print(f"    ✅ Avg response time: {avg_response_time:.2f}s")
            else:
                self.test_results[f"scalability_{load}"] = "❌ FAIL: All requests failed"
                print(f"    ❌ All {load} requests failed")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE AND LOAD TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if isinstance(r, dict) or r.startswith("✅")])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                print(f"  {test_name}:")
                for key, value in result.items():
                    print(f"    {key}: {value}")
            else:
                print(f"  {test_name}: {result}")
        
        # Performance recommendations
        print(f"\n💡 PERFORMANCE RECOMMENDATIONS:")
        
        if "response_times" in self.test_results and isinstance(self.test_results["response_times"], dict):
            avg_time = float(self.test_results["response_times"]["average"].replace("s", ""))
            if avg_time > 5.0:
                print("  ⚠️  Average response time is high (>5s). Consider optimizing prompts or using faster models.")
            elif avg_time < 2.0:
                print("  ✅ Response times are excellent (<2s).")
            else:
                print("  ✅ Response times are good (2-5s).")
        
        if "cost_analysis" in self.test_results and isinstance(self.test_results["cost_analysis"], dict):
            print("  💰 Cost optimization: Monitor token usage and consider prompt optimization.")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL PERFORMANCE TESTS PASSED! AI integration is performing well.")
        else:
            print(f"\n⚠️  {failed_tests} performance tests failed. Review the errors above.")
        
        print("\n" + "="*60)
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open("performance_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("📄 Performance test report saved to: performance_test_report.json")

# Main test runner
async def run_performance_tests(db_session):
    """Run the complete performance test suite"""
    test_suite = PerformanceTestSuite(db_session)
    await test_suite.run_all_performance_tests()

if __name__ == "__main__":
    # This would need to be run with a proper database session
    print("Performance tests require a database session to run.")
