#!/usr/bin/env python3
"""
تشغيل مباشر لمحتويات مجلد tool كما هي مع تطبيق منطق start.sh
"""

import os
import subprocess
import time
import threading
from datetime import datetime
import json

class DirectToolRunner:
    def __init__(self):
        self.processes = {}
        self.logs = {}
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command(self, cmd, name, background=True, timeout=None):
        """تشغيل أمر مع تسجيل النتائج"""
        try:
            if background:
                process = subprocess.Popen(cmd, shell=True, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         text=True)
                self.processes[name] = process
                self.log(f"✅ تم تشغيل {name} في الخلفية")
                return True
            else:
                result = subprocess.run(cmd, shell=True, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=timeout)
                self.logs[name] = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                return result.returncode == 0
        except Exception as e:
            self.log(f"❌ خطأ في تشغيل {name}: {str(e)}")
            return False
    
    def check_port(self, port):
        """فحص إذا كان المنفذ مفتوح"""
        try:
            result = subprocess.run(f"nc -z localhost {port}", 
                                  shell=True, capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def setup_directories(self):
        """إعداد المجلدات المطلوبة"""
        self.log("📁 إعداد المجلدات...")
        
        directories = ['/tmp/.X11-unix', '~/.vnc', '/tmp/logs']
        for directory in directories:
            expanded_dir = os.path.expanduser(directory)
            os.makedirs(expanded_dir, exist_ok=True)
            if directory == '/tmp/.X11-unix':
                os.chmod(expanded_dir, 0o1777)
        
        return True
    
    def start_virtual_display(self):
        """بدء العرض الافتراضي"""
        self.log("🖥️ محاولة بدء العرض الافتراضي...")
        
        # استخدام xvfb-run إذا كان متاحاً
        if os.system("command -v xvfb-run > /dev/null 2>&1") == 0:
            return self.run_command("xvfb-run -a -s '-screen 0 1024x768x24' sleep infinity", 
                                   "virtual_display")
        else:
            self.log("⚠️ xvfb-run غير متاح، تخطي العرض الافتراضي")
            return True
    
    def start_vnc_server(self):
        """بدء خادم VNC"""
        self.log("🔐 محاولة بدء خادم VNC...")
        
        if os.system("command -v x11vnc > /dev/null 2>&1") == 0:
            # إعداد كلمة مرور VNC
            vnc_passwd_cmd = "mkdir -p ~/.vnc && echo '123456' | x11vnc -storepasswd /dev/stdin ~/.vnc/passwd"
            self.run_command(vnc_passwd_cmd, "vnc_setup", background=False)
            
            # تشغيل x11vnc
            vnc_cmd = "x11vnc -display :0 -rfbauth ~/.vnc/passwd -forever -shared -rfbport 5900"
            return self.run_command(vnc_cmd, "vnc_server")
        else:
            self.log("⚠️ x11vnc غير متاح، تخطي خادم VNC")
            return True
    
    def start_websockify(self):
        """بدء websockify لتحويل VNC إلى WebSocket"""
        self.log("🌐 بدء websockify...")
        
        if os.path.exists('noVNC/utils/websockify/websockify.py'):
            websockify_cmd = "cd noVNC && python3 utils/websockify/websockify.py --web . 6080 localhost:5900"
            return self.run_command(websockify_cmd, "websockify")
        else:
            self.log("❌ websockify غير متاح")
            return False
    
    def start_http_server(self):
        """بدء خادم HTTP بديل"""
        self.log("🌍 بدء خادم HTTP على المنفذ 8080...")
        
        if os.path.exists('noVNC'):
            http_cmd = "cd noVNC && python3 -m http.server 8080"
            return self.run_command(http_cmd, "http_server")
        else:
            # إنشاء خادم HTTP بسيط
            simple_server = """
import http.server
import socketserver
import os

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head><meta charset="UTF-8"><title>سطح المكتب - Tool Runner</title></head>
<body style="font-family: Arial; text-align: center; background: #f0f0f0; padding: 50px;">
<h1>🖥️ سطح المكتب يعمل</h1>
<p>تم تشغيل محتويات مجلد tool بنجاح</p>
<p>الوقت: ''' + str(__import__('datetime').datetime.now()) + '''</p>
<p>المنفذ 8080 نشط</p>
</body></html>'''
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

os.chdir(os.path.dirname(__file__) or '.')
with socketserver.TCPServer(('0.0.0.0', 8080), SimpleHandler) as httpd:
    httpd.serve_forever()
"""
            with open('/tmp/simple_server.py', 'w') as f:
                f.write(simple_server)
            
            return self.run_command("python3 /tmp/simple_server.py", "simple_http")
    
    def start_cloudflared(self):
        """بدء cloudflared tunnel"""
        self.log("☁️ بدء cloudflared...")
        
        if os.path.exists('./cloudflared'):
            # أولوية للمنفذ 6080 (websockify)، ثم 8080 (HTTP)
            port = 6080 if self.check_port(6080) else 8080
            cloudflared_cmd = f"./cloudflared tunnel --url http://localhost:{port} --no-autoupdate"
            return self.run_command(cloudflared_cmd, "cloudflared")
        else:
            self.log("❌ cloudflared غير متاح")
            return False
    
    def get_cloudflared_url(self):
        """الحصول على رابط cloudflared"""
        self.log("🔗 البحث عن رابط cloudflared...")
        
        time.sleep(10)  # انتظار لبدء cloudflared
        
        try:
            # قراءة مخرجات cloudflared
            if 'cloudflared' in self.processes:
                process = self.processes['cloudflared']
                if process.poll() is None:  # العملية ما زالت تعمل
                    # محاولة قراءة الإخراج
                    output = ""
                    try:
                        stdout, stderr = process.communicate(timeout=5)
                        output = stdout + stderr
                    except:
                        # إذا لم تعمل، نبحث في ملفات السجل
                        if os.path.exists('/tmp/cloudflared.log'):
                            with open('/tmp/cloudflared.log', 'r') as f:
                                output = f.read()
                    
                    # البحث عن الرابط
                    import re
                    urls = re.findall(r'https://[-a-z0-9]*\.trycloudflare\.com', output)
                    if urls:
                        url = urls[0]
                        self.log(f"✅ تم العثور على الرابط: {url}")
                        
                        # حفظ الرابط
                        with open('desktop_link.txt', 'w') as f:
                            vnc_link = f"{url}/vnc.html?password=123456"
                            f.write(vnc_link)
                            
                        return url
        except Exception as e:
            self.log(f"❌ خطأ في الحصول على الرابط: {str(e)}")
        
        return None
    
    def create_status_report(self):
        """إنشاء تقرير الحالة"""
        self.log("📋 إنشاء تقرير الحالة...")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "tool_execution": "direct_mode",
            "processes": {},
            "ports": {},
            "files_status": {
                "dockerfile": os.path.exists('tool/Dockerfile'),
                "start_sh": os.path.exists('tool/start.sh'),
                "novnc": os.path.exists('noVNC'),
                "cloudflared": os.path.exists('./cloudflared')
            }
        }
        
        # فحص العمليات
        for name, process in self.processes.items():
            if process.poll() is None:
                status["processes"][name] = "running"
            else:
                status["processes"][name] = "stopped"
        
        # فحص المنافذ
        for port in [5900, 6080, 8080]:
            status["ports"][str(port)] = self.check_port(port)
        
        # حفظ التقرير
        with open('tool_execution_report.json', 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
        
        return status
    
    def run_all(self):
        """تشغيل جميع الخدمات"""
        self.log("🚀 بدء تشغيل جميع خدمات مجلد tool مباشرة")
        print("=" * 60)
        
        steps = [
            ("إعداد المجلدات", self.setup_directories),
            ("العرض الافتراضي", self.start_virtual_display),
            ("خادم VNC", self.start_vnc_server),
            ("WebSockify", self.start_websockify),
            ("خادم HTTP", self.start_http_server),
            ("CloudFlared", self.start_cloudflared)
        ]
        
        results = {}
        for step_name, step_func in steps:
            self.log(f"▶️ {step_name}...")
            results[step_name] = step_func()
            time.sleep(2)
        
        # الحصول على رابط cloudflared
        url = self.get_cloudflared_url()
        
        # إنشاء تقرير الحالة
        status = self.create_status_report()
        
        # عرض النتائج
        print("\n" + "=" * 60)
        self.log("🎉 انتهى تشغيل محتويات مجلد tool")
        print("=" * 60)
        
        print("\n📊 نتائج التشغيل:")
        for step, result in results.items():
            status_icon = "✅" if result else "❌"
            print(f"  {status_icon} {step}")
        
        print(f"\n🌐 حالة المنافذ:")
        for port, is_open in status["ports"].items():
            status_icon = "✅" if is_open else "❌"
            print(f"  {status_icon} المنفذ {port}")
        
        if url:
            print(f"\n🔗 الروابط المتاحة:")
            print(f"  🌍 الرابط الخارجي: {url}")
            print(f"  🖥️ سطح المكتب: {url}/vnc.html?password=123456")
            print(f"  📁 تم حفظ الرابط في: desktop_link.txt")
        
        print(f"\n📋 التقارير:")
        print(f"  📄 tool_execution_report.json - تقرير مفصل")
        
        return True

def main():
    """تشغيل الأداة الرئيسية"""
    runner = DirectToolRunner()
    
    try:
        success = runner.run_all()
        
        if success:
            print("\n🔁 إبقاء الخدمات نشطة...")
            print("⏹️ للإيقاف: Ctrl+C")
            
            # إبقاء البرنامج نشطاً
            while True:
                time.sleep(60)
                runner.log("الخدمات تعمل...")
                
        else:
            print("\n❌ فشل في تشغيل بعض الخدمات")
            return 1
            
    except KeyboardInterrupt:
        print("\n🔴 تم إيقاف الخدمات")
        return 0
    except Exception as e:
        print(f"\n💥 خطأ غير متوقع: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())