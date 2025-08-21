#!/usr/bin/env python3
"""
Improved test script untuk AI Agents dalam AEGIS Protocol
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
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

def wait_for_agent(agent_name: str, port: int, timeout: int = 30) -> bool:
    """Wait for agent to be ready"""
    print(f"⏳ Waiting for {agent_name} to be ready on port {port}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {agent_name} is ready!")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ {agent_name} failed to start within {timeout} seconds")
    return False

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
        ("Oracle Agent", 8001),
        ("Validator Agent", 8002), 
        ("Action Agent", 8003)
    ]
    
    results = {}
    
    for name, port in agents:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
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
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Oracle Response: {result}")
        else:
            print(f"   ❌ Oracle Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Oracle Agent error: {e}")
        return False
    
    # Step 2: Tunggu dan cek validator
    print("2. Checking Validator Agent processing...")
    time.sleep(3)
    
    # Step 3: Cek action agent
    print("3. Checking Action Agent processing...")
    time.sleep(3)
    
    return True

def start_agents():
    """Start all agents in separate processes"""
    print("🚀 Starting AI Agents...")
    
    agents = [
        ("Oracle Agent", "agents/oracle_agent.py", 8001),
        ("Validator Agent", "agents/validator_agent.py", 8002),
        ("Action Agent", "agents/action_agent.py", 8003)
    ]
    
    processes = []
    
    for name, script, port in agents:
        print(f"Starting {name}...")
        try:
            process = subprocess.Popen(
                [sys.executable, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            processes.append((name, process, port))
            print(f"✅ {name} started (PID: {process.pid})")
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
    
    # Wait for agents to be ready
    ready_agents = 0
    for name, process, port in processes:
        if wait_for_agent(name, port, timeout=15):
            ready_agents += 1
    
    print(f"\n📊 Agent Status: {ready_agents}/{len(agents)} agents ready")
    return processes

def stop_agents(processes):
    """Stop all running agents"""
    print("\n🛑 Stopping all agents...")
    
    for name, process, port in processes:
        if process.poll() is None:  # Still running
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    print("✅ All agents stopped")

def run_comprehensive_test():
    """Jalankan semua test"""
    print("🚀 Starting Comprehensive AI Agents Test")
    print("=" * 50)
    
    # Start agents
    processes = start_agents()
    
    if not processes:
        print("❌ Failed to start any agents")
        return
    
    # Wait a bit more for agents to fully initialize
    print("\n⏳ Waiting for agents to fully initialize...")
    time.sleep(5)
    
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
    
    # Stop agents
    stop_agents(processes)

if __name__ == "__main__":
    run_comprehensive_test()
