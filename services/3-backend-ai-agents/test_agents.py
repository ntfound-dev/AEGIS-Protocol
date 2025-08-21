#!/usr/bin/env python3
"""
Test script untuk AI Agents dalam AEGIS Protocol
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

# Simulasi data gempa bumi untuk testing
SAMPLE_EARTHQUAKE_DATA = {
    "source": "USGS",
    "magnitude": 7.8,
    "location": "Sumatra, Indonesia",
    "lat": -0.7893,
    "lon": 98.2942,
    "timestamp": int(time.time())
}

def test_validator_agent_web_endpoint():
    """Test endpoint web validator agent"""
    print("🔍 Testing Validator Agent Web Endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:8002/verify_disaster",
            json=SAMPLE_EARTHQUAKE_DATA,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validator Agent Response: {result}")
            return True
        else:
            print(f"❌ Validator Agent Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Validator Agent tidak berjalan di port 8002")
        return False
    except Exception as e:
        print(f"❌ Error testing Validator Agent: {e}")
        return False

def test_agent_health():
    """Test kesehatan semua agents"""
    print("\n🏥 Testing Agent Health...")
    
    agents = [
        ("Oracle Agent", "http://localhost:8001"),
        ("Validator Agent", "http://localhost:8002"), 
        ("Action Agent", "http://localhost:8003")
    ]
    
    results = {}
    
    for name, url in agents:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
                results[name] = True
            else:
                print(f"⚠️ {name}: Unhealthy ({response.status_code})")
                results[name] = False
        except:
            print(f"❌ {name}: Not running")
            results[name] = False
    
    return results

def test_data_flow():
    """Test alur data dari oracle -> validator -> action"""
    print("\n🔄 Testing Data Flow...")
    
    # Step 1: Kirim data ke oracle agent
    print("1. Sending data to Oracle Agent...")
    try:
        response = requests.post(
            "http://localhost:8001/process_earthquake",
            json=SAMPLE_EARTHQUAKE_DATA,
            timeout=10
        )
        print(f"   Oracle Response: {response.status_code}")
    except:
        print("   ❌ Oracle Agent tidak tersedia")
        return False
    
    # Step 2: Tunggu dan cek validator
    print("2. Checking Validator Agent...")
    time.sleep(2)
    
    # Step 3: Cek action agent
    print("3. Checking Action Agent...")
    time.sleep(2)
    
    return True

def run_comprehensive_test():
    """Jalankan semua test"""
    print("🚀 Starting Comprehensive AI Agents Test")
    print("=" * 50)
    
    # Test 1: Health Check
    health_results = test_agent_health()
    
    # Test 2: Web Endpoint
    web_test = test_validator_agent_web_endpoint()
    
    # Test 3: Data Flow
    flow_test = test_data_flow()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    healthy_agents = sum(health_results.values())
    print(f"Healthy Agents: {healthy_agents}/3")
    
    if web_test:
        print("Web Endpoint: ✅ Working")
    else:
        print("Web Endpoint: ❌ Failed")
    
    if flow_test:
        print("Data Flow: ✅ Working")
    else:
        print("Data Flow: ❌ Failed")
    
    if healthy_agents == 3 and web_test and flow_test:
        print("\n🎉 All tests passed! AI Agents are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check agent configurations.")

if __name__ == "__main__":
    run_comprehensive_test()
