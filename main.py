#!/usr/bin/env python3
"""
تشغيل نظام سطح المكتب البعيد - محاكي Dockerfile الأصلي
"""

import os
import sys
import subprocess
import threading
import time
import json
import socket
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

class DesktopEnvironment:
    def __init__(self):
        self.services = {}
        self.ports = {
            'vnc': 5900,
            'websocket': 6080, 
            'http': 8080
        }
        self.setup_environment()
    
    def log(self, message):
        """تسجيل الأحداث مع الوقت"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # كتابة في ملف السجل
        log_dir = Path("/tmp")
        log_file = log_dir / "desktop.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def setup_environment(self):
        """إعداد البيئة الأساسية"""
        self.log("🔧 إعداد البيئة الأساسية...")
        
        # إنشاء المجلدات المطلوبة
        directories = [
            "/tmp/.X11-unix",
            os.path.expanduser("~/.vnc"),
            "/tmp/logs",
            "noVNC"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if directory == "/tmp/.X11-unix":
                try:
                    os.chmod(directory, 0o1777)
                except:
                    pass
        
        # إعداد المنطقة الزمنية
        os.environ['TZ'] = 'Asia/Riyadh'
        os.environ['DISPLAY'] = ':1'
        
        self.log("✅ تم إعداد البيئة الأساسية")
    
    def download_dependencies(self):
        """تحميل المكونات المطلوبة"""
        self.log("📥 تحميل المكونات...")
        
        # تحميل noVNC إذا لم يكن موجود
        if not os.path.exists("noVNC/vnc.html"):
            try:
                self.log("📥 تحميل noVNC...")
                subprocess.run([
                    "git", "clone", "--branch", "v1.2.0", 
                    "https://github.com/novnc/noVNC.git"
                ], check=True, capture_output=True)
                
                self.log("📥 تحميل websockify...")
                subprocess.run([
                    "git", "clone", 
                    "https://github.com/novnc/websockify",
                    "noVNC/utils/websockify"
                ], check=True, capture_output=True)
                
                self.log("✅ تم تحميل noVNC و websockify")
            except Exception as e:
                self.log(f"⚠️ تحذير: {e}")
        
        # تحميل cloudflared إذا لم يكن موجود
        if not os.path.exists("cloudflared"):
            try:
                self.log("📥 تحميل cloudflared...")
                subprocess.run([
                    "wget", "-q",
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
                    "-O", "cloudflared"
                ], check=True)
                os.chmod("cloudflared", 0o755)
                self.log("✅ تم تحميل cloudflared")
            except Exception as e:
                self.log(f"⚠️ تحذير: {e}")
    
    def setup_vnc_password(self):
        """إعداد كلمة مرور VNC"""
        try:
            vnc_dir = os.path.expanduser("~/.vnc")
            subprocess.run([
                "x11vnc", "-storepasswd", "123456", f"{vnc_dir}/passwd"
            ], check=True, capture_output=True)
            self.log("✅ تم إعداد كلمة مرور VNC")
        except:
            # إنشاء ملف كلمة المرور يدوياً
            vnc_dir = os.path.expanduser("~/.vnc")
            with open(f"{vnc_dir}/passwd", "w") as f:
                f.write("123456")
            self.log("✅ تم إعداد كلمة مرور VNC (fallback)")
    
    def start_virtual_display(self):
        """تشغيل الشاشة الوهمية"""
        self.log("🖥️ [3/12] تشغيل Xvfb...")
        try:
            # محاولة تشغيل Xvfb
            subprocess.Popen([
                "Xvfb", ":1", "-screen", "0", "1024x768x16"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            self.log("✅ Xvfb يعمل")
            return True
        except:
            self.log("⚠️ Xvfb غير متاح - استخدام بديل")
            return False
    
    def start_desktop_environment(self):
        """تشغيل بيئة سطح المكتب"""
        self.log("🧠 [4/12] تشغيل بيئة سطح المكتب...")
        
        # محاولة تشغيل LXDE
        try:
            subprocess.Popen([
                "startlxde"
            ], stdout=open("/tmp/lxde.log", "w"), stderr=subprocess.STDOUT)
            time.sleep(2)
            self.log("✅ LXDE يعمل")
            return True
        except:
            # محاولة تشغيل fluxbox كبديل
            try:
                subprocess.Popen([
                    "fluxbox"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)
                self.log("✅ Fluxbox يعمل كبديل")
                return True
            except:
                self.log("⚠️ لا توجد بيئة سطح مكتب متاحة")
                return False
    
    def start_browser(self):
        """تشغيل المتصفح"""
        self.log("🌐 [4.5/12] تشغيل المتصفح...")
        
        browsers = ["google-chrome", "chromium", "chromium-browser"]
        for browser in browsers:
            try:
                subprocess.Popen([
                    browser, "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"
                ], stdout=open("/tmp/chrome.log", "w"), stderr=subprocess.STDOUT)
                time.sleep(3)
                
                # فحص إذا كان يعمل
                result = subprocess.run(["pgrep", browser.split("-")[0]], capture_output=True)
                if result.returncode == 0:
                    self.log(f"✅ {browser} يعمل")
                    return True
            except:
                continue
        
        self.log("⚠️ لا يوجد متصفح متاح")
        return False
    
    def start_vnc_server(self):
        """تشغيل خادم VNC"""
        self.log("🔐 [5/12] تشغيل x11vnc...")
        
        try:
            # إعداد كلمة المرور أولاً
            self.setup_vnc_password()
            
            # تشغيل x11vnc
            subprocess.Popen([
                "x11vnc", "-display", ":1", "-passwd", "123456", 
                "-forever", "-shared", "-noxdamage"
            ], stdout=open("/tmp/x11vnc.log", "w"), stderr=subprocess.STDOUT)
            
            time.sleep(2)
            self.log("✅ x11vnc يعمل على المنفذ 5900")
            return True
            
        except Exception as e:
            self.log(f"❌ فشل تشغيل x11vnc: {e}")
            return False
    
    def start_websockify(self):
        """تشغيل websockify"""
        self.log("🌐 [6/12] تشغيل websockify...")
        
        websockify_dir = "noVNC/utils/websockify"
        if os.path.exists(websockify_dir):
            try:
                # تشغيل websockify مباشرة
                subprocess.Popen([
                    "python3", "-m", "websockify",
                    "--web", "../..",
                    "6080", "localhost:5900"
                ], cwd=websockify_dir, stdout=open("/tmp/novnc.log", "w"), stderr=subprocess.STDOUT)
                
                time.sleep(2)
                self.log("✅ websockify يعمل على المنفذ 6080")
                return True
            except Exception as e:
                self.log(f"❌ فشل تشغيل websockify: {e}")
                return False
        else:
            self.log("❌ websockify غير موجود")
            return False
    
    def start_http_server(self):
        """تشغيل خادم HTTP"""
        self.log("🌍 [7/12] تشغيل خادم HTTP على المنفذ 8080...")
        
        try:
            def run_server():
                os.chdir("noVNC")
                subprocess.run([
                    "python3", "-m", "http.server", "8080"
                ], stdout=open("/tmp/http.log", "w"), stderr=subprocess.STDOUT)
            
            threading.Thread(target=run_server, daemon=True).start()
            time.sleep(2)
            self.log("✅ خادم HTTP يعمل على المنفذ 8080")
            return True
            
        except Exception as e:
            self.log(f"❌ فشل تشغيل خادم HTTP: {e}")
            return False
    
    def check_novnc_health(self):
        """فحص صحة noVNC"""
        self.log("🧪 [8/12] التحقق من تشغيل noVNC على المنفذ 6080...")
        
        # انتظار قليل لبدء الخدمة
        time.sleep(3)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 6080))
            sock.close()
            
            if result == 0:
                self.log("✅ noVNC يعمل على المنفذ 6080")
                return True
            else:
                self.log("❌ noVNC لا يعمل! فحص السجل...")
                try:
                    with open("/tmp/novnc.log", "r") as f:
                        log_content = f.read()
                        if log_content:
                            self.log(f"سجل websockify: {log_content[-200:]}")
                except:
                    pass
                return False
        except:
            self.log("❌ لا يمكن فحص noVNC")
            return False
    
    def start_cloudflared(self):
        """تشغيل cloudflared"""
        self.log("☁️ [9/12] تشغيل cloudflared...")
        
        if os.path.exists("./cloudflared"):
            try:
                subprocess.Popen([
                    "./cloudflared", "tunnel", 
                    "--url", "http://localhost:6080",
                    "--no-autoupdate",
                    "--metrics", "localhost:0"
                ], stdout=open("/tmp/cloudflared.log", "w"), stderr=subprocess.STDOUT)
                
                time.sleep(10)  # انتظار لإنشاء النفق
                self.log("✅ cloudflared يعمل")
                return True
            except Exception as e:
                self.log(f"❌ فشل تشغيل cloudflared: {e}")
                return False
        else:
            self.log("⚠️ cloudflared غير موجود")
            return False
    
    def extract_cloudflare_url(self):
        """استخراج رابط Cloudflare"""
        self.log("🔗 [10/12] استخراج رابط Cloudflare...")
        
        try:
            with open("/tmp/cloudflared.log", "r") as f:
                content = f.read()
                
            import re
            pattern = r'https://[\w-]+\.trycloudflare\.com'
            matches = re.findall(pattern, content)
            
            if matches:
                url = matches[0]
                self.log("📡 رابط سطح المكتب عبر Cloudflare:")
                self.log(url)
                self.log("")
                self.log("🖥️ رابط vnc.html الجاهز:")
                vnc_url = f"{url}/vnc.html?host={url.replace('https://', '')}&port=443&encrypt=1"
                self.log(vnc_url)
                return url
            else:
                self.log("❌ لم يتم العثور على الرابط")
                return None
                
        except Exception as e:
            self.log(f"❌ خطأ في استخراج الرابط: {e}")
            return None
    
    def run_full_system(self):
        """تشغيل النظام الكامل"""
        self.log("==== بدء تشغيل النظام ====")
        
        # الخطوة 1-2: التحميل والإعداد
        self.download_dependencies()
        
        # الخطوة 3: الشاشة الوهمية
        display_ok = self.start_virtual_display()
        
        # الخطوة 4: سطح المكتب
        desktop_ok = self.start_desktop_environment()
        
        # الخطوة 4.5: المتصفح
        browser_ok = self.start_browser()
        
        # الخطوة 5: VNC
        vnc_ok = self.start_vnc_server()
        
        # الخطوة 6: WebSocket
        websocket_ok = self.start_websockify()
        
        # الخطوة 7: HTTP
        http_ok = self.start_http_server()
        
        # الخطوة 8: فحص الصحة
        health_ok = self.check_novnc_health()
        
        # الخطوة 9: CloudFlared
        cloudflare_ok = self.start_cloudflared()
        
        # الخطوة 10: استخراج الرابط
        if cloudflare_ok:
            self.extract_cloudflare_url()
        
        # تقرير النتائج
        self.log("============================================================")
        self.log("🎉 تقرير النظام:")
        services = {
            "الشاشة الوهمية": display_ok,
            "سطح المكتب": desktop_ok, 
            "المتصفح": browser_ok,
            "VNC Server": vnc_ok,
            "WebSocket": websocket_ok,
            "HTTP Server": http_ok,
            "صحة noVNC": health_ok,
            "CloudFlared": cloudflare_ok
        }
        
        working_services = 0
        for service, status in services.items():
            status_icon = "✅" if status else "❌"
            self.log(f"  {status_icon} {service}")
            if status:
                working_services += 1
        
        self.log(f"🚀 الخدمات العاملة: {working_services}/{len(services)}")
        
        if working_services >= 4:  # إذا كان نصف الخدمات يعمل على الأقل
            self.log("🌐 النظام جاهز للاستخدام!")
            self.log("🔗 الروابط:")
            self.log("  💻 محلي: http://localhost:8080")
            self.log("  🖥️ VNC: http://localhost:6080/vnc.html")
            
            # إبقاء النظام نشط
            self.log("🔁 [11/12] إبقاء النظام نشط...")
            try:
                while True:
                    time.sleep(60)
                    self.log("💗 النظام يعمل...")
            except KeyboardInterrupt:
                self.log("🛑 إيقاف النظام...")
        else:
            self.log("❌ فشل تشغيل النظام - خدمات غير كافية")
            return 1
        
        return 0

def main():
    desktop = DesktopEnvironment()
    return desktop.run_full_system()

if __name__ == "__main__":
    sys.exit(main())