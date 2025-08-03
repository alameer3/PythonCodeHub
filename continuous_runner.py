#!/usr/bin/env python3
# تشغيل مستمر للكود من mycode.txt
import os
import subprocess
import time
import signal
import sys
from datetime import datetime

class ContinuousRunner:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def run_command_background(self, cmd, name):
        """تشغيل أمر في الخلفية مع متابعة"""
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes[name] = process
            self.log(f"✅ تم تشغيل {name}: {cmd}")
            return process
        except Exception as e:
            self.log(f"❌ فشل تشغيل {name}: {str(e)}")
            return None
    
    def check_process(self, name):
        """فحص حالة العملية"""
        if name in self.processes:
            process = self.processes[name]
            if process.poll() is None:
                return True
            else:
                self.log(f"⚠️ العملية {name} توقفت")
                return False
        return False
    
    def restart_process(self, name, cmd):
        """إعادة تشغيل العملية إذا توقفت"""
        if not self.check_process(name):
            self.log(f"🔄 إعادة تشغيل {name}")
            self.run_command_background(cmd, name)
    
    def setup_services(self):
        """إعداد الخدمات الأساسية"""
        self.log("🚀 بدء إعداد الخدمات المستمرة")
        
        # تحضير البيئة
        os.makedirs("~/.vnc", exist_ok=True)
        os.environ["DISPLAY"] = ":1"
        
        # تشغيل cloudflared
        cloudflared_cmd = "./cloudflared tunnel --url http://localhost:6080 --no-autoupdate"
        self.run_command_background(cloudflared_cmd, "cloudflared")
        
        # تشغيل noVNC proxy
        novnc_cmd = "python3 noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080"
        self.run_command_background(novnc_cmd, "novnc")
        
        # انتظار قليل للتأكد من بدء الخدمات
        time.sleep(5)
        
    def monitor_services(self):
        """مراقبة الخدمات وإعادة تشغيلها عند الحاجة"""
        self.log("👁️ بدء مراقبة الخدمات")
        
        while self.running:
            try:
                # فحص cloudflared
                self.restart_process("cloudflared", "./cloudflared tunnel --url http://localhost:6080 --no-autoupdate")
                
                # فحص noVNC
                self.restart_process("novnc", "python3 noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080")
                
                # عرض الحالة كل 30 ثانية
                self.log("💚 الخدمات تعمل بشكل طبيعي")
                self.print_status()
                
                # انتظار قبل الفحص التالي
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.log("⏹️ تم إيقاف المراقبة")
                self.shutdown()
                break
            except Exception as e:
                self.log(f"❌ خطأ في المراقبة: {str(e)}")
                time.sleep(10)
    
    def print_status(self):
        """طباعة حالة الخدمات"""
        self.log("📊 حالة الخدمات:")
        for name, process in self.processes.items():
            if process.poll() is None:
                self.log(f"  ✅ {name}: يعمل")
            else:
                self.log(f"  ❌ {name}: متوقف")
        
        # محاولة قراءة رابط cloudflared
        try:
            if os.path.exists("cloudflared.log"):
                with open("cloudflared.log", "r") as f:
                    content = f.read()
                    import re
                    match = re.search(r"https://.*\.trycloudflare\.com", content)
                    if match:
                        url = match.group(0)
                        self.log(f"🌐 الرابط: {url}/vnc.html?password=123456")
        except:
            pass
    
    def shutdown(self):
        """إيقاف جميع العمليات"""
        self.log("🔄 إيقاف جميع العمليات...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                self.log(f"✅ تم إيقاف {name}")
            except:
                try:
                    process.kill()
                    self.log(f"🔥 تم إنهاء {name} قسرياً")
                except:
                    pass
    
    def signal_handler(self, signum, frame):
        """معالج الإشارات للإيقاف الآمن"""
        self.log("⚠️ تم استلام إشارة الإيقاف")
        self.shutdown()
        sys.exit(0)

def main():
    """الدالة الرئيسية"""
    runner = ContinuousRunner()
    
    # تسجيل معالج الإشارات
    signal.signal(signal.SIGINT, runner.signal_handler)
    signal.signal(signal.SIGTERM, runner.signal_handler)
    
    try:
        # إعداد الخدمات
        runner.setup_services()
        
        # بدء المراقبة المستمرة
        runner.monitor_services()
        
    except Exception as e:
        runner.log(f"💥 خطأ عام: {str(e)}")
        runner.shutdown()

if __name__ == "__main__":
    main()