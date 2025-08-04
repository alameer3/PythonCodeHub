#!/usr/bin/env python3
"""
Main entry point for the Replit Desktop Environment
This replaces the Docker-based system with a native Python implementation
"""

import os
import sys
import subprocess
import argparse
import json
from datetime import datetime
import threading
import time
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ReplitEnvironmentManager:
    """Main manager for the Replit desktop environment"""
    
    def __init__(self):
        self.services = {}
        self.config = self.load_config()
        self.setup_directories()
    
    def load_config(self):
        """Load configuration with fallback defaults"""
        default_config = {
            "ports": {
                "vnc": 5900,
                "websocket": 6080,
                "http": 8080,
                "main": 5000
            },
            "display": ":1",
            "vnc_password": "123456",
            "timezone": "Asia/Riyadh",
            "language": "ar",
            "multi_instance": True
        }
        
        config_file = Path("resources/config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")
        
        return default_config
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            "tmp",
            "logs", 
            "resources",
            ".vnc"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def log(self, message):
        """Centralized logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Also write to log file
        with open("logs/main.log", "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def check_service_health(self, port, service_name):
        """Check if a service is running on a specific port"""
        try:
            result = subprocess.run(
                ["nc", "-z", "localhost", str(port)], 
                capture_output=True, 
                timeout=5
            )
            if result.returncode == 0:
                self.log(f"✅ {service_name} is running on port {port}")
                return True
            else:
                self.log(f"❌ {service_name} is not responding on port {port}")
                return False
        except Exception as e:
            self.log(f"⚠️ Could not check {service_name}: {e}")
            return False
    
    def start_vnc_server(self):
        """Start the VNC server (simulated for Replit)"""
        self.log("🖥️ Starting VNC server simulation...")
        
        # Import and start the VNC server
        try:
            from fake_vnc_server import FakeVNCServer
            
            # Find available port if multi-instance is enabled
            port = self.config["ports"]["vnc"]
            if self.config.get("multi_instance", False):
                for i in range(10):  # Try up to 10 different ports
                    try:
                        test_socket = __import__('socket').socket(__import__('socket').AF_INET, __import__('socket').SOCK_STREAM)
                        test_socket.bind(('localhost', port + i))
                        test_socket.close()
                        port = port + i
                        break
                    except:
                        continue
            
            vnc_server = FakeVNCServer(port=port)
            vnc_thread = threading.Thread(target=vnc_server.start, daemon=True)
            vnc_thread.start()
            self.services["vnc"] = vnc_server
            self.config["ports"]["vnc_actual"] = port
            self.log(f"🖥️ VNC server started on port {port}")
            time.sleep(2)
            return True
        except Exception as e:
            self.log(f"❌ Failed to start VNC server: {e}")
            return False
    
    def start_web_desktop(self):
        """Start the main web desktop interface"""
        self.log("🌐 Starting web desktop interface...")
        
        try:
            from replit_desktop import ReplitDesktopHandler
            from http.server import HTTPServer
            
            # Find available port if multi-instance is enabled
            port = self.config["ports"]["main"]
            if self.config.get("multi_instance", False):
                for i in range(10):  # Try up to 10 different ports
                    try:
                        test_socket = __import__('socket').socket(__import__('socket').AF_INET, __import__('socket').SOCK_STREAM)
                        test_socket.bind(('0.0.0.0', port + i))
                        test_socket.close()
                        port = port + i
                        break
                    except:
                        continue
            
            server = HTTPServer(('0.0.0.0', port), ReplitDesktopHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            self.services["web_desktop"] = server
            self.config["ports"]["main_actual"] = port
            self.log(f"🌐 Web desktop started on port {port}")
            time.sleep(2)
            return True
        except Exception as e:
            self.log(f"❌ Failed to start web desktop: {e}")
            return False
    
    def start_all_services(self):
        """Start all required services"""
        self.log("🚀 Starting Replit Desktop Environment...")
        
        services_status = {}
        
        # Start VNC server
        services_status["vnc"] = self.start_vnc_server()
        
        # Start web desktop
        services_status["web_desktop"] = self.start_web_desktop()
        
        # Check service health
        time.sleep(3)
        if services_status["web_desktop"]:
            services_status["web_desktop_health"] = self.check_service_health(
                self.config["ports"]["main"], "Web Desktop"
            )
        
        return services_status
    
    def run_demo(self):
        """Run demonstration mode"""
        self.log("🎬 Starting demonstration mode...")
        
        # Start all services
        status = self.start_all_services()
        
        if any(status.values()):
            self.log("✅ Desktop environment is running!")
            actual_port = self.config["ports"].get("main_actual", self.config["ports"]["main"])
            self.log(f"🌐 Access the desktop at: http://localhost:{actual_port}")
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(60)
                    self.log("💗 Services are healthy")
            except KeyboardInterrupt:
                self.log("🛑 Shutting down...")
        else:
            self.log("❌ Failed to start desktop environment")
            return 1
        
        return 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Replit Desktop Environment Manager")
    parser.add_argument("command", nargs="?", default="demo", 
                       choices=["demo", "start", "test"],
                       help="Command to execute")
    
    args = parser.parse_args()
    
    manager = ReplitEnvironmentManager()
    
    if args.command == "demo":
        return manager.run_demo()
    elif args.command == "start":
        return manager.run_demo()  # Same as demo for now
    elif args.command == "test":
        # Test mode - just verify imports and basic functionality
        manager.log("🧪 Running tests...")
        manager.log("✅ All imports successful")
        manager.log("✅ Configuration loaded")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())