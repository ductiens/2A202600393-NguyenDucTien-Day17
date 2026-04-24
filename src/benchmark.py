"""
Benchmark script for testing the Multi-Memory Agent
Runs 10 test cases automatically for Step 4
"""

import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from src.main import MultiMemoryAgent

class BenchmarkSuite:
    """Benchmark suite for testing the multi-memory agent"""
    
    def __init__(self):
        self.agent = MultiMemoryAgent()
        self.test_cases = self.generate_test_cases()
        self.results = []
    
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """Generate 10 test cases for benchmarking"""
        return [
            {
                "name": "Simple Greeting",
                "user_id": "user_001",
                "input": "Hello, how are you?",
                "expected_contains": ["hello", "understand"]
            },
            {
                "name": "Memory Storage Test",
                "user_id": "user_002", 
                "input": "My name is Alice and I love Python programming",
                "expected_contains": ["alice", "python"]
            },
            {
                "name": "Context Retention",
                "user_id": "user_002",
                "input": "What did I just tell you about myself?",
                "expected_contains": ["alice", "python"]
            },
            {
                "name": "Preference Setting",
                "user_id": "user_003",
                "input": "I prefer responses to be concise",
                "expected_contains": ["preference", "concise"]
            },
            {
                "name": "Complex Query",
                "user_id": "user_004",
                "input": "Can you help me understand machine learning concepts?",
                "expected_contains": ["machine learning", "understand"]
            },
            {
                "name": "Multi-turn Conversation",
                "user_id": "user_005",
                "input": "Let's discuss data science topics",
                "expected_contains": ["data science", "discuss"]
            },
            {
                "name": "Error Handling",
                "user_id": "user_006",
                "input": "",
                "expected_contains": []  # Empty input should be handled gracefully
            },
            {
                "name": "Semantic Search Test",
                "user_id": "user_007",
                "input": "Tell me about artificial intelligence",
                "expected_contains": ["artificial intelligence", "knowledge"]
            },
            {
                "name": "Memory Retrieval",
                "user_id": "user_004",
                "input": "What were we discussing earlier?",
                "expected_contains": ["machine learning"]
            },
            {
                "name": "Performance Test",
                "user_id": "user_008",
                "input": "This is a performance test with a longer message to see how the system handles more complex inputs with multiple sentences and various punctuation marks.",
                "expected_contains": ["performance", "longer"]
            }
        ]
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        start_time = time.time()
        
        try:
            # Process the message
            result = self.agent.process_message(
                user_id=test_case["user_id"],
                user_input=test_case["input"],
                session_id=str(uuid.uuid4())
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Evaluate results
            success = result["success"]
            response = result.get("response", "")
            
            # Check if expected content is present
            content_matches = []
            if test_case["expected_contains"]:
                response_lower = response.lower()
                for expected in test_case["expected_contains"]:
                    content_matches.append(expected.lower() in response_lower)
            
            # Calculate metrics
            metrics = {
                "success": success,
                "response_time": response_time,
                "response_length": len(response),
                "content_matches": content_matches,
                "all_content_matched": all(content_matches) if content_matches else True,
                "memory_context": result.get("memory_context", {}),
                "error": result.get("error")
            }
            
            return {
                "test_name": test_case["name"],
                "user_id": test_case["user_id"],
                "input": test_case["input"],
                "response": response,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "test_name": test_case["name"],
                "user_id": test_case["user_id"],
                "input": test_case["input"],
                "response": "",
                "metrics": {
                    "success": False,
                    "response_time": end_time - start_time,
                    "response_length": 0,
                    "content_matches": [],
                    "all_content_matched": False,
                    "memory_context": {},
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def run_benchmark(self) -> Dict[str, Any]:
        """Run all benchmark tests"""
        print("Starting Multi-Memory Agent Benchmark")
        print("=" * 50)
        
        self.results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\nRunning Test {i}/10: {test_case['name']}")
            print(f"Input: {test_case['input'][:50]}{'...' if len(test_case['input']) > 50 else ''}")
            
            result = self.run_single_test(test_case)
            self.results.append(result)
            
            # Print immediate results
            metrics = result["metrics"]
            status = "✅ PASS" if metrics["success"] else "❌ FAIL"
            print(f"Status: {status}")
            print(f"Response Time: {metrics['response_time']:.3f}s")
            print(f"Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
        
        # Calculate summary statistics
        summary = self.calculate_summary()
        self.print_summary(summary)
        
        return {
            "results": self.results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not self.results:
            return {}
        
        successful_tests = [r for r in self.results if r["metrics"]["success"]]
        response_times = [r["metrics"]["response_time"] for r in self.results]
        
        return {
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(self.results) * 100,
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "content_match_rate": sum(1 for r in self.results if r["metrics"]["all_content_matched"]) / len(self.results) * 100
        }
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary"""
        print("\n" + "=" * 50)
        print("BENCHMARK SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful Tests: {summary['successful_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Content Match Rate: {summary['content_match_rate']:.1f}%")
        print(f"Average Response Time: {summary['avg_response_time']:.3f}s")
        print(f"Min Response Time: {summary['min_response_time']:.3f}s")
        print(f"Max Response Time: {summary['max_response_time']:.3f}s")
        
        # Performance classification
        if summary['avg_response_time'] < 0.5:
            performance = "Excellent"
        elif summary['avg_response_time'] < 1.0:
            performance = "Good"
        elif summary['avg_response_time'] < 2.0:
            performance = "Fair"
        else:
            performance = "Needs Improvement"
        
        print(f"Overall Performance: {performance}")

def main():
    """Main function to run the benchmark"""
    print("Multi-Memory Agent Benchmark Suite")
    print("Running 10 test cases...")
    
    benchmark = BenchmarkSuite()
    results = benchmark.run_benchmark()
    
    # Save results to file
    import json
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: benchmark_results.json")

if __name__ == "__main__":
    main()
