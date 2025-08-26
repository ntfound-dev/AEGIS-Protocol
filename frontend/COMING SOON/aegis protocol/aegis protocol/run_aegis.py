# run_aegis.py
# Launcher script untuk Aegis Protocol System

import os
import sys
import subprocess
import webbrowser
import time
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'websockets',
        'aiohttp'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n📦 Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'enhanced_main.py',
        'orchestrator.py', 
        'base_agent.py',
        'api_server.py'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print("❌ Missing required files:")
        for file in missing:
            print(f"   - {file}")
        print("\n📁 Make sure all Python files from your Aegis Protocol are in the current directory")
        return False
    
    return True

def create_dashboard_html():
    """Create dashboard HTML file if it doesn't exist"""
    dashboard_path = Path("dashboard.html")
    
    if dashboard_path.exists():
        return True
    
    print("📄 Creating dashboard.html...")
    
    # You would copy the HTML content from the artifact here
    # For now, create a simple redirect
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Aegis Protocol Dashboard</title>
    <meta http-equiv="refresh" content="0; url=/docs">
</head>
<body>
    <h1>🛡️ Aegis Protocol</h1>
    <p>Redirecting to API documentation...</p>
    <p>Dashboard will be available soon at <a href="/">this link</a></p>
</body>
</html>"""
    
    with open(dashboard_path, 'w') as f:
        f.write(html_content)
    
    print("✅ Dashboard HTML created")
    return True

def run_api_server(host="127.0.0.1", port=8080, reload=True):
    """Run the FastAPI server"""
    print(f"🚀 Starting Aegis Protocol API Server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    
    try:
        # Import and run server
        import uvicorn
        uvicorn.run(
            "api_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
    
    return True

def run_enhanced_system():
    """Run enhanced system directly (without API)"""
    print("🚀 Running Enhanced Aegis System directly...")
    
    try:
        from enhanced_main import main
        import asyncio
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        return False
    
    return True

def open_dashboard(port=8080, delay=3):
    """Open dashboard in browser"""
    url = f"http://localhost:{port}"
    
    print(f"⏳ Waiting {delay} seconds for server to start...")
    time.sleep(delay)
    
    print(f"🌐 Opening dashboard: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"   Please open manually: {url}")

def show_banner():
    """Show startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🛡️  AEGIS PROTOCOL                                  ║
║                     AI-Powered Disaster Response System                      ║
║                                                                              ║
║  🎯 Real-time disaster detection    📱 Automated notifications              ║
║  🤖 AI validation & consensus       💰 Parametric insurance                 ║
║  🏛️ DAO governance system          📊 Performance monitoring               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(description="🛡️ Aegis Protocol Launcher")
    parser.add_argument("--mode", choices=["api", "direct", "demo"], default="api",
                       help="Run mode: api (with web UI), direct (CLI only), or demo")
    parser.add_argument("--host", default="127.0.0.1", help="API server host")
    parser.add_argument("--port", type=int, default=8080, help="API server port")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    show_banner()
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    
    if args.mode in ["api", "demo"]:
        if not check_dependencies():
            sys.exit(1)
    
    if not check_files():
        print("\n💡 Tip: Make sure you have all the Python files from your Aegis Protocol")
        print("   Copy them to the same directory as this launcher script")
        sys.exit(1)
    
    if args.mode == "api":
        create_dashboard_html()
        print("✅ Pre-flight checks passed\n")
        
        # Open browser in background
        if not args.no_browser:
            import threading
            browser_thread = threading.Thread(
                target=open_dashboard, 
                args=(args.port,), 
                daemon=True
            )
            browser_thread.start()
        
        # Run API server
        success = run_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
        
        if not success:
            print("\n🆘 API server failed to start")
            print("Try running in direct mode: python run_aegis.py --mode direct")
    
    elif args.mode == "direct":
        print("✅ Pre-flight checks passed\n")
        run_enhanced_system()
    
    elif args.mode == "demo":
        print("✅ Running in demo mode\n")
        print("🎭 Demo mode features:")
        print("   - Simulated disaster scenarios")
        print("   - Mock AI responses") 
        print("   - Performance metrics")
        print("   - Full UI experience")
        
        if not args.no_browser:
            import threading
            browser_thread = threading.Thread(
                target=open_dashboard,
                args=(args.port,),
                daemon=True
            )
            browser_thread.start()
        
        # Create minimal demo API
        create_demo_api(args.host, args.port)

def create_demo_api(host, port):
    """Create minimal demo API for showcase"""
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        import uvicorn
        
        demo_app = FastAPI(title="Aegis Protocol Demo")
        
        @demo_app.get("/", response_class=HTMLResponse)
        async def demo_dashboard():
            return """
            <html>
            <head><title>🛡️ Aegis Protocol Demo</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 50px;">
                <h1>🛡️ Aegis Protocol Demo</h1>
                <h2>AI-Powered Disaster Response System</h2>
                <p>This is a demo version showcasing the Aegis Protocol capabilities.</p>
                <div style="margin: 30px;">
                    <button onclick="alert('🎯 Jakarta Flood simulation started!')" 
                            style="margin: 10px; padding: 15px 30px; font-size: 16px;">
                        🌊 Simulate Jakarta Flood
                    </button>
                    <button onclick="alert('🚨 Earthquake M6.2 simulation started!')"
                            style="margin: 10px; padding: 15px 30px; font-size: 16px;">
                        🌍 Simulate Earthquake
                    </button>
                    <button onclick="alert('🔥 Forest fire simulation started!')"
                            style="margin: 10px; padding: 15px 30px; font-size: 16px;">
                        🔥 Simulate Forest Fire
                    </button>
                </div>
                <div style="margin-top: 40px;">
                    <h3>📊 System Status</h3>
                    <p>🟢 System: OPERATIONAL (Demo Mode)</p>
                    <p>📡 DON Monitoring: ACTIVE</p>
                    <p>💰 Vault: $10,000,000</p>
                    <p>🎯 Active Events: 0</p>
                </div>
                <div style="margin-top: 40px;">
                    <p><a href="/docs">📚 View API Documentation</a></p>
                </div>
            </body>
            </html>
            """
        
        @demo_app.get("/api/status")
        async def demo_status():
            return {
                "status": "operational",
                "mode": "demo",
                "active_events": 0,
                "vault_balance": 10000000,
                "don_monitoring": True
            }
        
        print("🎭 Starting demo server...")
        uvicorn.run(demo_app, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Demo server error: {e}")

if __name__ == "__main__":
    main()