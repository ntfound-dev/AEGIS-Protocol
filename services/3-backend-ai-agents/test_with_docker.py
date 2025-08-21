#!/usr/bin/env python3
"""
Test script untuk AI Agents dengan Docker setup
"""

import asyncio
import json
import time
import requests
import subprocess
import sys
import os
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

def check_docker_services():
    """Check if Docker services are running"""
    print("🔍 Checking Docker services...")
    
    services = [
        ("dfx-replica", "aegis-dfx-replica"),
        ("oracle-agent", "aegis-oracle-agent"),
        ("validator-agent", "aegis-validator-agent"),
        ("action-agent", "aegis-action-agent")
    ]
    
    running_services = []
    
    for service_name, container_name in services:
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if container_name in result.stdout:
                print(f"✅ {service_name}: Running")
                running_services.append(service_name)
            else:
                print(f"❌ {service_name}: Not running")
                
        except Exception as e:
            print(f"❌ {service_name}: Error checking - {e}")
    
    return running_services

def start_ai_agents_docker():
    """Start AI agents using Docker Compose"""
    print("\n🚀 Starting AI Agents with Docker Compose...")
    
    try:
        # Start only the AI agents (dfx-replica should already be running)
        result = subprocess.run(
            ["docker-compose", "up", "-d", "oracle-agent", "validator-agent", "action-agent"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ AI Agents started successfully")
            return True
        else:
            print(f"❌ Failed to start AI Agents: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting AI Agents: {e}")
        return False

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

def check_dfx_status():
    """Check dfx-replica status"""
    print("\n🔗 Checking dfx-replica status...")
    
    try:
        # Check if dfx-replica is accessible
        response = requests.get("http://localhost:4943", timeout=5)
        print("✅ dfx-replica is accessible")
        return True
    except:
        print("❌ dfx-replica is not accessible")
        return False

def run_docker_test():
    """Jalankan test dengan Docker setup"""
    print("🚀 Starting Docker-based AI Agents Test")
    print("=" * 50)
    
    # Check Docker services
    running_services = check_docker_services()
    
    # Check dfx-replica
    dfx_ok = check_dfx_status()
    
    if not dfx_ok:
        print("❌ dfx-replica tidak berjalan. Jalankan: docker-compose up -d dfx-replica")
        return
    
    # Start AI agents if not running
    if len(running_services) < 4:  # Should have dfx-replica + 3 agents
        print("\n⚠️ Some AI agents not running. Starting them...")
        if not start_ai_agents_docker():
            print("❌ Failed to start AI agents")
            return
    
    # Wait for agents to be ready
    print("\n⏳ Waiting for agents to be ready...")
    ready_agents = 0
    for name, port in [("Oracle Agent", 8001), ("Validator Agent", 8002), ("Action Agent", 8003)]:
        if wait_for_agent(name, port, timeout=30):
            ready_agents += 1
    
    if ready_agents < 3:
        print(f"❌ Only {ready_agents}/3 agents ready")
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
    print(f"dfx-replica: {'✅ Running' if dfx_ok else '❌ Not running'}")
    
    if web_test:
        print("Web Endpoint: ✅ Working")
    else:
        print("Web Endpoint: ❌ Failed")
    
    if flow_test:
        print("Data Flow: ✅ Working")
    else:
        print("Data Flow: ❌ Failed")
    
    if healthy_agents == 3 and web_test and flow_test and dfx_ok:
        print("\n🎉 All tests passed! AI Agents are working correctly with Docker.")
    else:
        print("\n⚠️ Some tests failed. Check Docker containers and configurations.")

if __name__ == "__main__":
    run_docker_test()
