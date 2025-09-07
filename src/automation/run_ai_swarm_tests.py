#!/usr/bin/env python3
"""
Simple test runner for AI Swarm Testcontainers
Bypasses pytest compatibility issues
"""

import requests
import time
import json
import sys
from datetime import datetime

class AISwarmTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def assert_equal(self, actual, expected, message=""):
        if actual == expected:
            self.passed += 1
            return True
        else:
            self.failed += 1
            error_msg = f"Assertion failed: {message} - Expected: {expected}, Got: {actual}"
            self.errors.append(error_msg)
            self.log(error_msg, "ERROR")
            return False
    
    def assert_true(self, condition, message=""):
        if condition:
            self.passed += 1
            return True
        else:
            self.failed += 1
            error_msg = f"Assertion failed: {message} - Condition was False"
            self.errors.append(error_msg)
            self.log(error_msg, "ERROR")
            return False
    
    def wait_for_services(self, timeout=30):
        """Wait for AI Swarm services to be ready"""
        self.log("Waiting for AI Swarm services to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.log("✅ AI Swarm services are ready!")
                    return True
            except requests.exceptions.RequestException as e:
                pass
            time.sleep(2)
        
        self.log("❌ AI Swarm services failed to start within timeout", "ERROR")
        return False
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        self.log("🧪 Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            
            # Test status code
            self.assert_equal(response.status_code, 200, "Health endpoint status code")
            
            # Test response structure
            data = response.json()
            self.assert_true("status" in data, "Health response has 'status' field")
            self.assert_true("timestamp" in data, "Health response has 'timestamp' field")
            self.assert_true("service" in data, "Health response has 'service' field")
            self.assert_true("containers" in data, "Health response has 'containers' field")
            self.assert_true("database" in data, "Health response has 'database' field")
            
            # Test values
            self.assert_equal(data["status"], "healthy", "Service status should be 'healthy'")
            self.assert_equal(data["service"], "AI Swarm Docker", "Service name")
            self.assert_equal(data["database"], True, "Database should be available")
            
            # Test containers list
            expected_containers = ["swarm-master", "swarm-cache", "portainer"]
            for container in expected_containers:
                self.assert_true(container in data["containers"], f"Container '{container}' should be listed")
            
            self.log("✅ Health endpoint test completed")
            
        except Exception as e:
            self.failed += 1
            self.errors.append(f"Health endpoint test failed: {str(e)}")
            self.log(f"❌ Health endpoint test failed: {str(e)}", "ERROR")
    
    def test_status_endpoint(self):
        """Test the system status endpoint"""
        self.log("🧪 Testing status endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/status")
            
            # Test status code
            self.assert_equal(response.status_code, 200, "Status endpoint status code")
            
            # Test response structure
            data = response.json()
            self.assert_true("service" in data, "Status response has 'service' field")
            self.assert_true("version" in data, "Status response has 'version' field")
            self.assert_true("status" in data, "Status response has 'status' field")
            self.assert_true("integrations" in data, "Status response has 'integrations' field")
            self.assert_true("events" in data, "Status response has 'events' field")
            
            # Test values
            self.assert_equal(data["service"], "AI Swarm Intelligence System", "Service name")
            self.assert_equal(data["version"], "2.0 Docker", "Service version")
            self.assert_equal(data["status"], "running", "Service status")
            self.assert_true(isinstance(data["integrations"], int), "Integrations should be an integer")
            self.assert_true(isinstance(data["events"], int), "Events should be an integer")
            
            self.log("✅ Status endpoint test completed")
            
        except Exception as e:
            self.failed += 1
            self.errors.append(f"Status endpoint test failed: {str(e)}")
            self.log(f"❌ Status endpoint test failed: {str(e)}", "ERROR")
    
    def test_response_times(self):
        """Test API response times"""
        self.log("🧪 Testing response times...")
        
        endpoints = ["/health", "/status"]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                self.assert_equal(response.status_code, 200, f"{endpoint} status code")
                self.assert_true(response_time < 2.0, f"{endpoint} response time should be < 2.0s (was {response_time:.3f}s)")
                
                self.log(f"✅ {endpoint}: {response_time:.3f}s")
                
            except Exception as e:
                self.failed += 1
                self.errors.append(f"Response time test for {endpoint} failed: {str(e)}")
                self.log(f"❌ Response time test for {endpoint} failed: {str(e)}", "ERROR")
    
    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        self.log("🧪 Testing concurrent requests...")
        
        import concurrent.futures
        
        def make_health_request():
            try:
                return requests.get(f"{self.base_url}/health", timeout=10)
            except Exception as e:
                return None
        
        try:
            # Make 10 concurrent requests (reduced from 20 to be less aggressive)
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_health_request) for _ in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # Count successful requests
            success_count = sum(1 for response in results if response and response.status_code == 200)
            
            self.assert_true(success_count >= 8, f"At least 8/10 concurrent requests should succeed (got {success_count})")
            self.log(f"✅ Concurrent test: {success_count}/10 requests successful")
            
        except Exception as e:
            self.failed += 1
            self.errors.append(f"Concurrent requests test failed: {str(e)}")
            self.log(f"❌ Concurrent requests test failed: {str(e)}", "ERROR")
    
    def test_system_workflow(self):
        """Test complete system workflow"""
        self.log("🧪 Testing full system workflow...")
        
        try:
            # 1. Check health
            health_response = requests.get(f"{self.base_url}/health")
            self.assert_equal(health_response.status_code, 200, "Health check in workflow")
            
            health_data = health_response.json()
            self.assert_equal(health_data["status"], "healthy", "System health status")
            
            # 2. Check status
            status_response = requests.get(f"{self.base_url}/status")
            self.assert_equal(status_response.status_code, 200, "Status check in workflow")
            
            status_data = status_response.json()
            self.assert_equal(status_data["status"], "running", "System running status")
            
            # 3. Test rapid requests
            for i in range(5):
                response = requests.get(f"{self.base_url}/health")
                self.assert_equal(response.status_code, 200, f"Rapid request {i+1}")
            
            self.log("✅ Full system workflow test completed successfully!")
            
        except Exception as e:
            self.failed += 1
            self.errors.append(f"System workflow test failed: {str(e)}")
            self.log(f"❌ System workflow test failed: {str(e)}", "ERROR")
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("🚀 Starting AI Swarm Testcontainers Test Suite")
        self.log("=" * 60)
        
        # Wait for services
        if not self.wait_for_services():
            self.log("❌ Services not available - aborting tests", "ERROR")
            return False
        
        # Run individual tests
        self.test_health_endpoint()
        self.test_status_endpoint()
        self.test_response_times()
        self.test_concurrent_requests()
        self.test_system_workflow()
        
        # Print summary
        self.log("=" * 60)
        self.log(f"📊 Test Results Summary:")
        self.log(f"   ✅ Passed: {self.passed}")
        self.log(f"   ❌ Failed: {self.failed}")
        self.log(f"   📈 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        
        if self.errors:
            self.log("🔍 Errors Details:")
            for i, error in enumerate(self.errors, 1):
                self.log(f"   {i}. {error}")
        
        if self.failed == 0:
            self.log("🎉 All tests passed! AI Swarm Testcontainers integration is working perfectly!")
            return True
        else:
            self.log(f"⚠️ {self.failed} test(s) failed. Please review the errors above.")
            return False

def main():
    """Main test runner"""
    tester = AISwarmTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()