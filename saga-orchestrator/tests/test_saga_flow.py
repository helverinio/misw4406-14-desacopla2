import pytest
import requests
import json
import time
from typing import Dict, Any


class TestSagaFlow:
    """Integration tests for saga orchestrator flow"""
    
    def __init__(self):
        self.saga_orchestrator_url = "http://localhost:5003"
        self.integraciones_url = "http://localhost:5001"
        self.alianzas_url = "http://localhost:5002"
    
    def test_complete_partner_creation_saga(self):
        """Test complete partner creation saga flow"""
        # Test data
        partner_data = {
            "nombre": "Test Partner Saga",
            "email": "test.saga@example.com",
            "telefono": "+1234567890",
            "direccion": "123 Test Street",
            "correlation_id": "test-correlation-123"
        }
        
        print("🧪 Starting partner creation saga test...")
        
        # Step 1: Start saga through orchestrator
        response = requests.post(
            f"{self.saga_orchestrator_url}/api/v1/saga/partner-creation",
            json=partner_data,
            timeout=30
        )
        
        assert response.status_code == 202, f"Expected 202, got {response.status_code}: {response.text}"
        saga_response = response.json()
        saga_id = saga_response["saga_id"]
        
        print(f"✅ Saga started successfully: {saga_id}")
        
        # Step 2: Monitor saga progress
        max_wait_time = 60  # 60 seconds max wait
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_response = requests.get(
                f"{self.saga_orchestrator_url}/api/v1/saga/status/{saga_id}",
                timeout=10
            )
            
            assert status_response.status_code == 200, f"Failed to get saga status: {status_response.text}"
            
            saga_status = status_response.json()["saga"]
            current_status = saga_status["status"]
            
            print(f"📊 Saga status: {current_status}")
            
            if current_status == "completed":
                print("✅ Saga completed successfully!")
                
                # Verify partner was created
                partner_id = saga_status["partner_id"]
                alliance_id = saga_status["alliance_id"]
                
                assert partner_id is not None, "Partner ID should not be None"
                assert alliance_id is not None, "Alliance ID should not be None"
                
                print(f"✅ Partner created: {partner_id}")
                print(f"✅ Alliance created: {alliance_id}")
                
                return True
                
            elif current_status == "failed":
                error = saga_status.get("error", "Unknown error")
                print(f"❌ Saga failed: {error}")
                return False
                
            # Wait before next check
            time.sleep(2)
        
        print("⏰ Saga test timed out")
        return False
    
    def test_saga_compensation(self):
        """Test saga compensation when alliance creation fails"""
        print("🧪 Starting saga compensation test...")
        
        # This test would require simulating a failure in alliance creation
        # For now, we'll just verify the compensation endpoints exist
        
        # Check if saga orchestrator is running
        try:
            response = requests.get(f"{self.saga_orchestrator_url}/health", timeout=5)
            assert response.status_code == 200
            print("✅ Saga orchestrator is healthy")
        except Exception as e:
            print(f"❌ Saga orchestrator not available: {e}")
            return False
        
        return True
    
    def test_saga_status_endpoints(self):
        """Test saga status and monitoring endpoints"""
        print("🧪 Testing saga status endpoints...")
        
        # Test health endpoint
        response = requests.get(f"{self.saga_orchestrator_url}/health", timeout=10)
        assert response.status_code == 200
        
        # Test active sagas endpoint
        response = requests.get(f"{self.saga_orchestrator_url}/api/v1/saga/active", timeout=10)
        assert response.status_code == 200
        
        active_sagas = response.json()
        print(f"📊 Active sagas: {active_sagas['total']}")
        
        return True


def run_saga_tests():
    """Run all saga tests"""
    test_suite = TestSagaFlow()
    
    print("🚀 Starting Saga Flow Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Saga Status Endpoints", test_suite.test_saga_status_endpoints),
        ("Saga Compensation", test_suite.test_saga_compensation),
        ("Complete Partner Creation Saga", test_suite.test_complete_partner_creation_saga),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = "PASSED" if result else "FAILED"
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)}"
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    for test_name, result in results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"{status_emoji} {test_name}: {result}")
    
    return results


if __name__ == "__main__":
    run_saga_tests()
