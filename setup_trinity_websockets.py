#!/usr/bin/env python3
"""
Trinity WebSocket Setup - Multiple VNC Proxy Configuration
Sets up websockify for multiple Trinity Android VMs
"""

import subprocess
import time
import os
import signal
from pathlib import Path

class TrinityWebSocketSetup:
    def __init__(self):
        self.novnc_dir = Path("noVNC_integrated")
        self.websocket_processes = []
        
    def log(self, message):
        print(f"[WebSocket Setup] {message}")
        
    def kill_existing_websockets(self):
        """إنهاء جميع عمليات websockify الموجودة"""
        try:
            result = subprocess.run(['pkill', '-f', 'websockify'], capture_output=True)
            if result.returncode == 0:
                self.log("✅ Killed existing websocket processes")
            time.sleep(2)
        except:
            pass
            
    def start_websocket_proxy(self, web_port, vnc_port, description):
        """تشغيل websocket proxy لمنفذ VNC محدد"""
        cmd = [
            "python3", "-m", "websockify",
            "--web", str(self.novnc_dir),
            "--verbose",
            f"0.0.0.0:{web_port}",
            f"localhost:{vnc_port}"
        ]
        
        self.log(f"🌐 Starting WebSocket for {description} (Web:{web_port} -> VNC:{vnc_port})")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # انتظار قصير للتأكد من بدء العملية
            time.sleep(2)
            
            if process.poll() is None:  # العملية تعمل
                self.log(f"✅ WebSocket running for {description}")
                self.websocket_processes.append({
                    'process': process,
                    'web_port': web_port,
                    'vnc_port': vnc_port,
                    'description': description
                })
                return True
            else:
                self.log(f"❌ Failed to start WebSocket for {description}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error starting WebSocket for {description}: {e}")
            return False
            
    def setup_multi_websockets(self):
        """إعداد websockets متعددة للـ Trinity VMs"""
        self.log("🚀 Setting up Trinity WebSocket proxies...")
        
        # إنهاء العمليات الموجودة
        self.kill_existing_websockets()
        
        # تكوين WebSocket proxies
        configs = [
            (5000, 5900, "Desktop Environment"),    # الأساسي
            (5001, 5910, "Android Main"),           # Trinity VM 1
            (5002, 5911, "Android Gaming"),         # Trinity VM 2  
            (5003, 5912, "Android Dev"),            # Trinity VM 3
            (5004, 5902, "Android Demo")            # النسخة التجريبية
        ]
        
        successful = 0
        for web_port, vnc_port, description in configs:
            if self.start_websocket_proxy(web_port, vnc_port, description):
                successful += 1
                
        self.log(f"🎉 Setup complete: {successful}/{len(configs)} WebSocket proxies running")
        
        if successful > 0:
            self.log("🌐 Access URLs:")
            self.log("   📋 Main Interface: http://localhost:5000/trinity.html")
            self.log("   📱 Android Main: http://localhost:5001/vnc.html")
            self.log("   🎮 Android Gaming: http://localhost:5002/vnc.html")
            self.log("   💻 Android Dev: http://localhost:5003/vnc.html")
            self.log("   🧪 Android Demo: http://localhost:5004/vnc.html")
            
        return successful > 0
        
    def monitor_websockets(self):
        """مراقبة WebSocket processes"""
        self.log("👁️ Monitoring WebSocket processes...")
        
        while True:
            try:
                time.sleep(30)
                
                active_count = 0
                for ws in self.websocket_processes:
                    if ws['process'].poll() is None:
                        active_count += 1
                    else:
                        self.log(f"⚠️ WebSocket for {ws['description']} stopped")
                        
                self.log(f"💗 WebSocket Status: {active_count}/{len(self.websocket_processes)} active")
                
            except KeyboardInterrupt:
                self.log("🛑 Stopping WebSocket monitoring...")
                break
            except Exception as e:
                self.log(f"❌ Monitoring error: {e}")
                
    def cleanup(self):
        """تنظيف العمليات"""
        self.log("🧹 Cleaning up WebSocket processes...")
        for ws in self.websocket_processes:
            try:
                ws['process'].terminate()
                ws['process'].wait(timeout=5)
            except:
                try:
                    ws['process'].kill()
                except:
                    pass
                    
def main():
    setup = TrinityWebSocketSetup()
    
    try:
        if setup.setup_multi_websockets():
            setup.monitor_websockets()
        else:
            print("❌ Failed to setup WebSocket proxies")
            return 1
            
    except KeyboardInterrupt:
        setup.log("🛑 Received interrupt signal")
    finally:
        setup.cleanup()
        
    return 0

if __name__ == "__main__":
    exit(main())