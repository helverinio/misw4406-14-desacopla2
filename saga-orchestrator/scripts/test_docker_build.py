#!/usr/bin/env python3
"""
Test script to validate Docker build and basic functionality
"""

import subprocess
import sys
import time
import requests
import json

def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def test_docker_build():
    """Test Docker image build"""
    print("🐳 Testing Docker build...")
    
    success, stdout, stderr = run_command("docker build -t saga-orchestrator:test .")
    
    if success:
        print("✅ Docker build successful")
        return True
    else:
        print(f"❌ Docker build failed:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

def test_simple_compose():
    """Test simple docker-compose setup"""
    print("🚀 Testing simple docker-compose...")
    
    # Start services
    success, stdout, stderr = run_command("docker-compose -f docker-compose.simple.yml up -d")
    
    if not success:
        print(f"❌ Failed to start services:")
        print(f"STDERR: {stderr}")
        return False
    
    print("⏳ Waiting for services to be ready...")
    time.sleep(30)  # Wait for services to start
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5003/health", timeout=10)
        if response.status_code == 200:
            print("✅ Saga orchestrator is healthy")
            health_data = response.json()
            print(f"Health data: {json.dumps(health_data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to saga orchestrator: {e}")
        return False
    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        run_command("docker-compose -f docker-compose.simple.yml down")

def main():
    """Main test function"""
    print("🧪 Docker Build and Compose Test")
    print("=" * 40)
    
    tests = [
        ("Docker Build", test_docker_build),
        ("Simple Compose", test_simple_compose),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
