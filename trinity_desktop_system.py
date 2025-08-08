#!/usr/bin/env python3
"""
Trinity Desktop System - نظام متكامل يجمع بين TrinityEmulator ونظام سطح المكتب البعيد
يستفيد من remote-desktop-clients لتوفير واجهة VNC قوية
"""

import os
import sys
import subprocess
import threading
import time
import socket
import json
from datetime import datetime
from pathlib import Path

class TrinityDesktopSystem:
    def __init__(self):
        self.services = {}
        self.ports = {
            'vnc': 5900,
            'websocket': 5000,
            'trinity_gui': 8080,
            'adb': 5555
        }
        
        # Replit security configuration
        self.replit_config = {
            'bind_host': '0.0.0.0',  # Required for Replit
            'bind_port': 5000,       # Fixed port for Replit
            'environment': 'replit'
        }
        self.trinity_process = None
        self.setup_environment()
    
    def log(self, message):
        """تسجيل الأحداث مع الوقت"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # كتابة في ملف السجل
        log_file = Path("/tmp/trinity_desktop.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def setup_environment(self):
        """إعداد البيئة الأساسية"""
        self.log("🔧 إعداد البيئة للنظام المتكامل...")
        
        # إنشاء المجلدات المطلوبة
        directories = [
            "/tmp/.X11-unix",
            os.path.expanduser("~/.vnc"),
            "/tmp/logs",
            "/tmp/trinity",
            "noVNC_integrated"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if directory == "/tmp/.X11-unix":
                try:
                    os.chmod(directory, 0o1777)
                except:
                    pass
        
        # إعداد متغيرات البيئة للـ Replit
        os.environ['TZ'] = 'UTC'  # Safer for Replit environment
        os.environ['DISPLAY'] = ':1'
        os.environ['TRINITY_HOME'] = os.path.abspath('./TrinityEmulator')
        
        # Replit-specific environment variables
        os.environ['REPLIT_ENVIRONMENT'] = 'true'
        os.environ['WEBSOCKET_HOST'] = self.replit_config['bind_host']
        os.environ['WEBSOCKET_PORT'] = str(self.replit_config['bind_port'])
        
        self.log("✅ تم إعداد البيئة الأساسية")
    
    def setup_integrated_novnc(self):
        """إعداد noVNC متكامل مع remote-desktop-clients"""
        self.log("📱 إعداد نظام noVNC متكامل...")
        
        if not os.path.exists("noVNC_integrated"):
            try:
                self.log("📥 تحميل noVNC...")
                subprocess.run([
                    "git", "clone", "--branch", "v1.2.0", 
                    "https://github.com/novnc/noVNC.git", "noVNC_integrated"
                ], check=True, capture_output=True)
                
                self.log("📥 تحميل websockify...")
                subprocess.run([
                    "git", "clone", 
                    "https://github.com/novnc/websockify",
                    "noVNC_integrated/utils/websockify"
                ], check=True, capture_output=True)
                
                self.log("✅ تم تحميل noVNC")
            except Exception as e:
                self.log(f"⚠️ تحذير: {e}")
        
        # إنشاء صفحة مخصصة للنظام المتكامل
        self.create_trinity_interface()
        
    def create_trinity_interface(self):
        """إنشاء واجهة مخصصة للنظام المتكامل"""
        trinity_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Trinity Desktop System - النظام المتكامل</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            margin: 0; 
            padding: 20px; 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            text-align: center;
        }
        .header {
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .service-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        .service-card:hover {
            transform: translateY(-5px);
        }
        .service-title {
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #fff;
        }
        .service-description {
            color: rgba(255,255,255,0.8);
            margin-bottom: 15px;
        }
        .action-btn {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .action-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .vnc-frame {
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 10px;
            margin-top: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online { background: #2ecc71; }
        .status-offline { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ Trinity Desktop System</h1>
            <p>النظام المتكامل للمحاكاة وسطح المكتب البعيد</p>
        </div>
        
        <div class="services-grid">
            <div class="service-card">
                <div class="service-title">
                    <span class="status-indicator status-online"></span>
                    🎮 Trinity Emulator
                </div>
                <div class="service-description">
                    محاكي Android عالي الأداء مع تقنية Graphics Projection
                </div>
                <a href="/trinity/start" class="action-btn">🚀 بدء المحاكي</a>
                <a href="/trinity/status" class="action-btn">📊 حالة النظام</a>
            </div>
            
            <div class="service-card">
                <div class="service-title">
                    <span class="status-indicator status-online"></span>
                    🖥️ Remote Desktop
                </div>
                <div class="service-description">
                    نظام سطح المكتب البعيد مع دعم VNC, RDP, SPICE
                </div>
                <a href="/vnc.html" class="action-btn">💻 VNC Client</a>
                <a href="/touch.html" class="action-btn">📱 Touch Interface</a>
            </div>
            
            <div class="service-card">
                <div class="service-title">
                    <span class="status-indicator status-online"></span>
                    🔧 Development Tools
                </div>
                <div class="service-description">
                    أدوات التطوير وإدارة النظام
                </div>
                <a href="/adb/connect" class="action-btn">🔌 ADB Connection</a>
                <a href="/logs" class="action-btn">📋 System Logs</a>
            </div>
        </div>
        
        <div id="vnc-container">
            <h2>🌐 Remote Desktop Access</h2>
            <iframe src="/vnc.html?autoconnect=true&resize=scale" class="vnc-frame"></iframe>
        </div>
        
        <div class="status-section">
            <h3>⚡ System Status</h3>
            <div id="system-status">جاري تحديث الحالة...</div>
        </div>
    </div>
    
    <script>
        // تحديث حالة النظام
        function updateSystemStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('system-status').innerHTML = 
                        'Trinity: ' + (data.trinity ? '✅ Running' : '❌ Offline') + '<br>' +
                        'VNC: ' + (data.vnc ? '✅ Connected' : '❌ Disconnected') + '<br>' +
                        'ADB: ' + (data.adb ? '✅ Ready' : '❌ Not Ready');
                })
                .catch(error => {
                    document.getElementById('system-status').innerHTML = '❌ Status Update Failed';
                });
        }
        
        // تحديث كل 5 ثواني
        setInterval(updateSystemStatus, 5000);
        updateSystemStatus();
    </script>
</body>
</html>"""
        
        with open("noVNC_integrated/trinity.html", "w", encoding="utf-8") as f:
            f.write(trinity_html)
        
        self.log("✅ تم إنشاء واجهة Trinity المخصصة")
    
    def start_virtual_display(self):
        """تشغيل الشاشة الوهمية"""
        self.log("🖥️ إعداد X Display للنظام المتكامل...")
        
        current_display = os.environ.get('DISPLAY', ':1')
        os.environ['DISPLAY'] = current_display
        
        # فحص إذا كان X server يعمل
        try:
            result = subprocess.run(['xwininfo', '-root'], capture_output=True, timeout=5)
            if result.returncode == 0:
                self.log("✅ X Server يعمل")
                return True
        except:
            pass
        
        # تشغيل Xvfb
        try:
            subprocess.Popen([
                "Xvfb", ":1", "-screen", "0", "1920x1080x24",
                "-ac", "+extension", "GLX"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.environ['DISPLAY'] = ':1'
            time.sleep(3)
            self.log("✅ Xvfb يعمل على :1 (1920x1080)")
            return True
        except:
            self.log("⚠️ استخدام X server الحالي")
            return True
    
    def start_desktop_environment(self):
        """تشغيل بيئة سطح المكتب"""
        self.log("🧠 تشغيل بيئة سطح المكتب...")
        
        try:
            subprocess.Popen([
                "fluxbox"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log("✅ Fluxbox يعمل")
            return True
        except:
            self.log("⚠️ لا توجد بيئة سطح مكتب متاحة")
            return False
    
    def setup_vnc_password(self):
        """إعداد كلمة مرور VNC"""
        try:
            vnc_dir = os.path.expanduser("~/.vnc")
            subprocess.run([
                "x11vnc", "-storepasswd", "trinity123", f"{vnc_dir}/passwd"
            ], check=True, capture_output=True)
            self.log("✅ تم إعداد كلمة مرور VNC: trinity123")
        except:
            vnc_dir = os.path.expanduser("~/.vnc")
            with open(f"{vnc_dir}/passwd", "w") as f:
                f.write("trinity123")
            self.log("✅ تم إعداد كلمة مرور VNC (fallback)")
    
    def start_vnc_server(self):
        """تشغيل خادم VNC"""
        self.log("🔐 تشغيل VNC Server للنظام المتكامل...")
        
        try:
            subprocess.run(["pkill", "-f", "x11vnc"], capture_output=True)
            time.sleep(1)
            
            self.setup_vnc_password()
            display = os.environ.get('DISPLAY', ':1')
            
            subprocess.Popen([
                "x11vnc", 
                "-display", display,
                "-usepw",
                "-forever", "-shared", 
                "-noxdamage", "-noxfixes",
                "-rfbport", "5900",
                "-nap", "-wait", "50", "-defer", "1",
                "-autoport", "no"
            ], stdout=open("/tmp/x11vnc.log", "w"), stderr=subprocess.STDOUT)
            
            time.sleep(3)
            
            # فحص الاتصال
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5900))
                sock.close()
                
                if result == 0:
                    self.log("✅ VNC Server يعمل على المنفذ 5900")
                    return True
                else:
                    self.log("❌ VNC Server لا يعمل")
                    return False
            except:
                self.log("❌ لا يمكن فحص VNC Server")
                return False
                
        except Exception as e:
            self.log(f"❌ فشل تشغيل VNC Server: {e}")
            return False
    
    def start_websockify(self):
        """تشغيل websockify للـ noVNC"""
        self.log("🌐 تشغيل WebSocket للـ noVNC...")
        
        try:
            subprocess.run(["pkill", "-f", "websockify"], capture_output=True)
            time.sleep(1)
        except:
            pass
        
        try:
            env = os.environ.copy()
            # Set Python path to include the virtual environment
            env['PYTHONPATH'] = "./.pythonlibs/lib/python3.12/site-packages:" + env.get('PYTHONPATH', '')
            env['PATH'] = "./.pythonlibs/bin:" + env.get('PATH', '')
            
            # Create web directory if not exists
            web_dir = os.path.abspath("./noVNC_integrated")
            if not os.path.exists(web_dir):
                os.makedirs(web_dir, exist_ok=True)
            
            # Use the Python executable from the virtual environment
            python_exe = "./.pythonlibs/bin/python" if os.path.exists("./.pythonlibs/bin/python") else "python3"
            
            websockify_cmd = [
                python_exe, "-m", "websockify",
                "--web", web_dir,
                "--verbose",
                f"{self.replit_config['bind_host']}:{self.replit_config['bind_port']}", 
                "localhost:5900"
            ]
            
            self.log(f"🔧 تشغيل: {' '.join(websockify_cmd)}")
            
            process = subprocess.Popen(
                websockify_cmd,
                stdout=open("/tmp/websockify.log", "w"),
                stderr=subprocess.STDOUT,
                env=env,
                cwd="."
            )
            
            # Wait a bit and check if process is still running
            time.sleep(5)
            if process.poll() is None:
                self.log(f"✅ WebSocket يعمل على {self.replit_config['bind_host']}:{self.replit_config['bind_port']}")
                return True
            else:
                self.log("❌ WebSocket توقف مباشرة")
                return False
                
        except Exception as e:
            self.log(f"❌ فشل تشغيل WebSocket: {e}")
            return False
    
    def prepare_trinity_emulator(self):
        """إعداد Trinity Emulator للتشغيل"""
        self.log("🎮 إعداد Trinity Emulator...")
        
        # استخدام QEMU المثبت مع النظام
        try:
            result = subprocess.run(["qemu-system-x86_64", "--version"], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ QEMU متوفر وجاهز")
                self.log(f"📝 إصدار QEMU: {result.stdout.strip()}")
                return True
            else:
                self.log("❌ QEMU غير متاح")
                return False
        except Exception as e:
            self.log(f"❌ خطأ في فحص QEMU: {e}")
            return False
    
    def start_trinity_emulator(self):
        """تشغيل Trinity Emulator"""
        self.log("🚀 بدء تشغيل Trinity Emulator...")
        
        if not self.prepare_trinity_emulator():
            return False
        
        try:
            # استخدام QEMU المثبت
            qemu_executable = "qemu-system-x86_64"
            
            self.log(f"🎮 تشغيل Trinity باستخدام: {qemu_executable}")
            
            # إعداد مجلد للقرص الوهمي
            os.makedirs("/tmp/trinity", exist_ok=True)
            
            # فحص وجود Android ISO
            android_iso_path = "/tmp/trinity/android-x86.iso"
            if not os.path.exists(android_iso_path):
                self.log("❌ لم يتم العثور على Android ISO")
                return False
            
            # إنشاء قرص صلب للنظام
            android_disk_path = "/tmp/trinity/android_system.img"
            if not os.path.exists(android_disk_path):
                try:
                    subprocess.run([
                        "qemu-img", "create", "-f", "qcow2", 
                        android_disk_path, "4G"  # مساحة أكبر لنظام Android
                    ], check=True, capture_output=True)
                    self.log("✅ تم إنشاء قرص النظام لـ Android (4GB)")
                except Exception as e:
                    self.log(f"⚠️ خطأ في إنشاء قرص النظام: {e}")
                    return False
            
            self.log(f"📱 Android ISO متاح: {os.path.getsize(android_iso_path) // 1024 // 1024} MB")
            
            # إعداد أوامر التشغيل لـ Android (محسّنة لـ Replit)
            trinity_cmd = [
                qemu_executable,
                "-m", "256",    # ذاكرة قليلة جداً لـ Replit  
                "-display", "vnc=:2,password=off",  # VNC على display :2 (منفذ 5902)
                "-cdrom", android_iso_path,  # Android ISO كـ CDROM
                "-boot", "order=d",  # التمهيد من CD فقط
                "-vga", "std",      # كرت رسوميات قياسي
                "-machine", "pc",   # نوع الآلة القياسي
                "-cpu", "qemu64",   # معالج متوافق
                "-netdev", "user,id=net0",  # شبكة بسيطة
                "-device", "rtl8139,netdev=net0"  # كرت شبكة بسيط
            ]
            
            # تشغيل Trinity في thread منفصل
            def run_trinity():
                try:
                    self.trinity_process = subprocess.Popen(
                        trinity_cmd,
                        stdout=open("/tmp/trinity.log", "w"),
                        stderr=subprocess.STDOUT
                    )
                    
                    self.log("✅ Trinity Emulator يعمل")
                    self.trinity_process.wait()
                    
                except Exception as e:
                    self.log(f"❌ خطأ في تشغيل Trinity: {e}")
            
            trinity_thread = threading.Thread(target=run_trinity, daemon=True)
            trinity_thread.start()
            
            time.sleep(3)  # انتظار حتى يبدأ Trinity
            
            # فحص إذا كان المعالج يعمل
            if self.trinity_process and self.trinity_process.poll() is None:
                return True
            else:
                self.log("⚠️ Trinity توقف مباشرة")
                return False
                
        except Exception as e:
            self.log(f"❌ فشل تشغيل Trinity Emulator: {e}")
            return False
    
    def check_services_health(self):
        """فحص صحة جميع الخدمات"""
        self.log("🧪 فحص صحة النظام المتكامل...")
        
        services_status = {}
        
        # فحص VNC
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5900))
            sock.close()
            services_status['vnc'] = result == 0
        except:
            services_status['vnc'] = False
        
        # فحص WebSocket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            services_status['websocket'] = result == 0
        except:
            services_status['websocket'] = False
        
        # فحص Trinity
        services_status['trinity'] = self.trinity_process is not None and self.trinity_process.poll() is None
        
        return services_status
    
    def run_integrated_system(self):
        """تشغيل النظام المتكامل الكامل"""
        self.log("==== بدء النظام المتكامل Trinity Desktop ====")
        
        # الخطوة 1: إعداد noVNC المتكامل
        self.setup_integrated_novnc()
        
        # الخطوة 2: بدء الشاشة الوهمية
        display_ok = self.start_virtual_display()
        
        # الخطوة 3: بدء بيئة سطح المكتب
        desktop_ok = self.start_desktop_environment()
        
        # الخطوة 4: بدء VNC Server
        vnc_ok = self.start_vnc_server()
        
        # الخطوة 5: بدء WebSocket
        websocket_ok = self.start_websockify()
        
        # الخطوة 6: إعداد وتشغيل Trinity Emulator
        trinity_ok = self.start_trinity_emulator()
        
        # تقرير النتائج
        self.log("============================================================")
        self.log("🎉 تقرير النظام المتكامل:")
        services = {
            "Virtual Display": display_ok,
            "Desktop Environment": desktop_ok,
            "VNC Server": vnc_ok,
            "WebSocket/noVNC": websocket_ok,
            "Trinity Emulator": trinity_ok
        }
        
        working_services = 0
        for service, status in services.items():
            status_icon = "✅" if status else "❌"
            self.log(f"  {status_icon} {service}")
            if status:
                working_services += 1
        
        self.log(f"🚀 الخدمات العاملة: {working_services}/{len(services)}")
        
        if working_services >= 3:
            self.log("🌐 النظام المتكامل جاهز للاستخدام!")
            self.log("🔗 الروابط:")
            self.log("  ✨ الواجهة المتكاملة: http://localhost:5000/trinity.html")
            self.log("  💻 VNC Client العادي: http://localhost:5000/vnc.html")
            self.log("  📱 Touch Interface: http://localhost:5000/touch.html")
            self.log("  🎮 Trinity Emulator: VNC :5902 (localhost:5902)")
            self.log("  🔐 كلمة مرور VNC: trinity123")
            
            # إبقاء النظام نشط
            self.log("🔁 إبقاء النظام المتكامل نشط...")
            try:
                while True:
                    time.sleep(30)
                    health = self.check_services_health()
                    running_count = sum(1 for status in health.values() if status)
                    self.log(f"💗 النظام يعمل ({running_count}/{len(health)} خدمات)...")
                    
            except KeyboardInterrupt:
                self.log("🛑 إيقاف النظام...")
                if self.trinity_process:
                    self.trinity_process.terminate()
        else:
            self.log("❌ فشل تشغيل النظام المتكامل")
            return False
        
        return True

if __name__ == "__main__":
    system = TrinityDesktopSystem()
    system.run_integrated_system()