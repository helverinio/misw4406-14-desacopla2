#!/usr/bin/env python3
"""
Test saga integration by creating a partner and monitoring the complete flow
"""
import requests
import json
import time
import uuid
from datetime import datetime


def test_saga_integration():
    """Test complete saga integration"""
    
    # Service URLs
    saga_orchestrator_url = "http://localhost:5003"
    integraciones_url = "http://localhost:5001"
    
    print("🧪 Testing Saga Integration")
    print("=" * 50)
    
    # Test 1: Health checks
    print("\n1️⃣ Testing service health...")
    
    services = {
        "Saga Orchestrator": saga_orchestrator_url,
        "Gestion de Integraciones": integraciones_url
    }
    
    for service_name, url in services.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: Healthy")
            else:
                print(f"❌ {service_name}: Unhealthy ({response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {service_name}: Not available ({e})")
            return False
    
    # Test 2: Direct partner creation (traditional way)
    print("\n2️⃣ Testing direct partner creation...")
    
    partner_data_direct = {
        "nombre": f"Direct Partner {uuid.uuid4().hex[:8]}",
        "email": f"direct.{uuid.uuid4().hex[:8]}@example.com",
        "telefono": "+1234567890",
        "direccion": "123 Direct Street"
    }
    
    try:
        response = requests.post(
            f"{integraciones_url}/api/v1/partners",
            json=partner_data_direct,
            timeout=30
        )
        
        if response.status_code == 201:
            partner_response = response.json()
            partner_id = partner_response['partner']['id']
            print(f"✅ Direct partner created: {partner_id}")
        else:
            print(f"❌ Direct partner creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Direct partner creation error: {e}")
        return False
    
    # Test 3: Saga-based partner creation
    print("\n3️⃣ Testing saga-based partner creation...")
    
    correlation_id = f"test-{uuid.uuid4().hex[:8]}"
    partner_data_saga = {
        "nombre": f"Saga Partner {uuid.uuid4().hex[:8]}",
        "email": f"saga.{uuid.uuid4().hex[:8]}@example.com",
        "telefono": "+1234567891",
        "direccion": "456 Saga Street",
        "correlation_id": correlation_id
    }
    
    try:
        # Start saga
        response = requests.post(
            f"{saga_orchestrator_url}/api/v1/saga/partner-creation",
            json=partner_data_saga,
            timeout=30
        )
        
        if response.status_code == 202:
            saga_response = response.json()
            saga_id = saga_response['saga_id']
            print(f"✅ Saga started: {saga_id}")
            
            # Monitor saga progress
            print("📊 Monitoring saga progress...")
            max_wait = 60  # 60 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(
                    f"{saga_orchestrator_url}/api/v1/saga/status/{saga_id}",
                    timeout=10
                )
                
                if status_response.status_code == 200:
                    saga_status = status_response.json()['saga']
                    current_status = saga_status['status']
                    
                    print(f"   Status: {current_status}")
                    
                    if current_status == "completed":
                        partner_id = saga_status.get('partner_id')
                        alliance_id = saga_status.get('alliance_id')
                        print(f"✅ Saga completed successfully!")
                        print(f"   Partner ID: {partner_id}")
                        print(f"   Alliance ID: {alliance_id}")
                        break
                    elif current_status == "failed":
                        error = saga_status.get('error', 'Unknown error')
                        print(f"❌ Saga failed: {error}")
                        return False
                
                time.sleep(3)
            else:
                print("⏰ Saga monitoring timed out")
                return False
                
        else:
            print(f"❌ Saga creation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Saga creation error: {e}")
        return False
    
    # Test 4: Check active sagas
    print("\n4️⃣ Checking active sagas...")
    
    try:
        response = requests.get(f"{saga_orchestrator_url}/api/v1/saga/active", timeout=10)
        if response.status_code == 200:
            active_sagas = response.json()
            print(f"📊 Active sagas: {active_sagas['total']}")
        else:
            print(f"❌ Failed to get active sagas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting active sagas: {e}")
    
    print("\n✅ Saga integration test completed successfully!")
    return True


def test_saga_endpoints():
    """Test saga-specific endpoints in gestion-de-integraciones"""
    
    print("\n🧪 Testing Saga Endpoints in Gestion de Integraciones")
    print("=" * 50)
    
    integraciones_url = "http://localhost:5001"
    
    # Test saga partner creation endpoint
    partner_data = {
        "nombre": f"Saga Endpoint Test {uuid.uuid4().hex[:8]}",
        "email": f"saga.endpoint.{uuid.uuid4().hex[:8]}@example.com",
        "telefono": "+1234567892",
        "direccion": "789 Saga Endpoint Street"
    }
    
    try:
        response = requests.post(
            f"{integraciones_url}/api/v1/saga/partners",
            json=partner_data,
            timeout=30
        )
        
        if response.status_code == 202:
            saga_response = response.json()
            saga_id = saga_response['saga_id']
            print(f"✅ Saga endpoint test successful: {saga_id}")
            
            # Test saga status endpoint
            time.sleep(2)  # Wait a bit
            
            status_response = requests.get(
                f"{integraciones_url}/api/v1/saga/partners/saga-status/{saga_id}",
                timeout=10
            )
            
            if status_response.status_code == 200:
                print("✅ Saga status endpoint working")
            else:
                print(f"❌ Saga status endpoint failed: {status_response.status_code}")
                
        else:
            print(f"❌ Saga endpoint test failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Saga endpoint test error: {e}")
        return False
    
    return True


def main():
    """Run all saga tests"""
    
    print("🚀 Starting Comprehensive Saga Testing")
    print("=" * 60)
    
    tests = [
        ("Saga Integration Test", test_saga_integration),
        ("Saga Endpoints Test", test_saga_endpoints)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results[test_name] = "PASSED" if result else "FAILED"
        except Exception as e:
            results[test_name] = f"ERROR: {str(e)}"
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 Final Test Results:")
    for test_name, result in results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"{status_emoji} {test_name}: {result}")
    
    # Summary
    passed_tests = sum(1 for result in results.values() if result == "PASSED")
    total_tests = len(results)
    
    print(f"\n📈 Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Saga implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")


if __name__ == "__main__":
    main()
