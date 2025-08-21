#!/usr/bin/env python3
"""
Script untuk menjalankan semua AI Agents secara bersamaan
"""

import subprocess
import time
import signal
import sys
import os
from typing import List

class AgentRunner:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.agents = [
            {
                "name": "Oracle Agent",
                "script": "agents/oracle_agent.py",
                "port": 8001
            },
            {
                "name": "Validator Agent", 
                "script": "agents/validator_agent.py",
                "port": 8002
            },
            {
                "name": "Action Agent",
                "script": "agents/action_agent.py", 
                "port": 8003
            }
        ]
    
    def start_agent(self, agent_info: dict):
        """Start individual agent"""
        print(f"🚀 Starting {agent_info['name']} on port {agent_info['port']}...")
        
        try:
            process = subprocess.Popen(
                [sys.executable, agent_info['script']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(process)
            print(f"✅ {agent_info['name']} started (PID: {process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to start {agent_info['name']}: {e}")
    
    def start_all_agents(self):
        """Start all agents"""
        print("🎯 Starting All AI Agents...")
        print("=" * 50)
        
        for agent in self.agents:
            self.start_agent(agent)
            time.sleep(2)  # Delay between starts
        
        print("\n" + "=" * 50)
        print("📊 Agent Status:")
        for i, process in enumerate(self.processes):
            status = "Running" if process.poll() is None else "Stopped"
            print(f"  {self.agents[i]['name']}: {status}")
    
    def stop_all_agents(self):
        """Stop all running agents"""
        print("\n🛑 Stopping all agents...")
        
        for i, process in enumerate(self.processes):
            if process.poll() is None:  # Still running
                print(f"Stopping {self.agents[i]['name']}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All agents stopped")
    
    def monitor_agents(self):
        """Monitor agent status"""
        try:
            while True:
                print("\n" + "-" * 30)
                print("📊 Agent Status Monitor:")
                print("-" * 30)
                
                all_running = True
                for i, process in enumerate(self.processes):
                    status = "Running" if process.poll() is None else "Stopped"
                    print(f"  {self.agents[i]['name']}: {status}")
                    if process.poll() is not None:
                        all_running = False
                
                if not all_running:
                    print("\n⚠️ Some agents have stopped!")
                    break
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
            self.stop_all_agents()

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print("\n🛑 Received interrupt signal")
    if hasattr(signal_handler, 'runner'):
        signal_handler.runner.stop_all_agents()
    sys.exit(0)

def main():
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run agent runner
    runner = AgentRunner()
    signal_handler.runner = runner  # Store reference for signal handler
    
    try:
        # Start all agents
        runner.start_all_agents()
        
        # Wait a bit for agents to initialize
        print("\n⏳ Waiting for agents to initialize...")
        time.sleep(5)
        
        # Monitor agents
        runner.monitor_agents()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        runner.stop_all_agents()

if __name__ == "__main__":
    main()
