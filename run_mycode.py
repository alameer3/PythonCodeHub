#!/usr/bin/env python3
# تشغيل الكود من ملف mycode.txt بشكل صارم
import os
import subprocess
import time
import re
import sys

def run_command(cmd, description=""):
    """تشغيل أمر shell مع طباعة النتيجة"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ نجح: {cmd}")
            if result.stdout:
                print(f"النتيجة: {result.stdout.strip()}")
        else:
            print(f"❌ فشل: {cmd}")
            if result.stderr:
                print(f"الخطأ: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ انتهت المهلة الزمنية للأمر: {cmd}")
        return False
    except Exception as e:
        print(f"💥 خطأ في تشغيل الأمر: {cmd} - {str(e)}")
        return False

def main():
    """تشغيل الكود الأصلي من mycode.txt بأقصى ما يمكن في بيئة Replit"""
    
    print("🚀 بدء تشغيل الكود من mycode.txt بشكل صارم")
    print("=" * 60)
    
    # المرحلة 1: التحديث والتثبيت
    print("\n📦 المرحلة 1: محاولة التحديث والتثبيت")
    run_command("apt update -y 2>/dev/null || echo 'تحديث النظام غير مسموح في Replit'", "تحديث النظام")
    
    # محاولة تثبيت الحزم المطلوبة (ستفشل في Replit لكن سنحاول)
    packages = ["lxde", "x11vnc", "xvfb", "git", "websockify", "wget", "firefox", "tigervnc-standalone-server"]
    print(f"\n🔧 محاولة تثبيت الحزم: {', '.join(packages)}")
    for package in packages:
        run_command(f"apt install -y {package} 2>/dev/null || echo 'حزمة {package} غير متوفرة'", f"تثبيت {package}")
    
    # المرحلة 2: إعداد VNC
    print("\n🔐 المرحلة 2: إعداد كلمة مرور VNC")
    run_command("mkdir -p ~/.vnc", "إنشاء مجلد VNC")
    run_command("echo '123456' | vncpasswd -f > ~/.vnc/passwd 2>/dev/null || echo 'vncpasswd غير متوفر'", "إعداد كلمة المرور")
    run_command("chmod 600 ~/.vnc/passwd 2>/dev/null || echo 'ملف كلمة المرور غير موجود'", "تعديل صلاحيات كلمة المرور")
    
    # المرحلة 3: إعداد الشاشة الوهمية
    print("\n🖥️ المرحلة 3: إعداد الشاشة الوهمية")
    run_command("Xvfb :1 -screen 0 1024x768x16 & 2>/dev/null || echo 'Xvfb غير متوفر'", "تشغيل الشاشة الوهمية")
    os.environ["DISPLAY"] = ":1"
    print("✅ تم تعيين متغير DISPLAY إلى :1")
    
    # المرحلة 4: تشغيل LXDE
    print("\n🚀 المرحلة 4: تشغيل LXDE")
    run_command("startlxde & 2>/dev/null || echo 'LXDE غير متوفر'", "تشغيل سطح المكتب")
    
    # المرحلة 5: تشغيل Firefox
    print("\n🌐 المرحلة 5: تشغيل Firefox")
    run_command("firefox & 2>/dev/null || echo 'Firefox غير متوفر'", "تشغيل المتصفح")
    
    # المرحلة 6: تحميل noVNC
    print("\n🌀 المرحلة 6: تحميل noVNC")
    if not os.path.exists("noVNC"):
        run_command("git clone https://github.com/novnc/noVNC.git", "تحميل noVNC")
    else:
        print("✅ مجلد noVNC موجود بالفعل")
    
    if not os.path.exists("noVNC/utils/websockify"):
        run_command("git clone https://github.com/novnc/websockify noVNC/utils/websockify", "تحميل websockify")
    else:
        print("✅ مجلد websockify موجود بالفعل")
    
    # المرحلة 7: تشغيل noVNC
    print("\n✅ المرحلة 7: تشغيل noVNC")
    if os.path.exists("noVNC/utils/launch.sh"):
        run_command("nohup ./noVNC/utils/launch.sh --vnc localhost:5900 --listen 6080 & 2>/dev/null || echo 'فشل تشغيل noVNC'", "تشغيل noVNC")
    else:
        print("❌ ملف launch.sh غير موجود")
    
    # المرحلة 8: تحميل وتشغيل Cloudflared
    print("\n🌐 المرحلة 8: تحميل وتشغيل Cloudflared")
    if not os.path.exists("cloudflared"):
        run_command("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared", "تحميل Cloudflared")
        run_command("chmod +x cloudflared", "تعديل صلاحيات Cloudflared")
    else:
        print("✅ ملف cloudflared موجود بالفعل")
    
    # تشغيل Cloudflared في الخلفية
    run_command("./cloudflared tunnel --url http://localhost:6080 --no-autoupdate > cloudflared.log 2>&1 &", "تشغيل Cloudflared")
    
    # المرحلة 9: البحث عن الرابط
    print("\n⏳ المرحلة 9: انتظار الرابط الخارجي")
    print("انتظار 10 ثوانٍ للرابط...")
    time.sleep(10)
    
    try:
        if os.path.exists("cloudflared.log"):
            with open("cloudflared.log", "r") as f:
                log_content = f.read()
            
            print("📋 محتوى ملف cloudflared.log:")
            print(log_content[:500] + "..." if len(log_content) > 500 else log_content)
            
            # البحث عن الرابط
            match = re.search(r"https://.*\.trycloudflare\.com", log_content)
            if match:
                url = match.group(0)
                print(f"\n✅ رابط سطح المكتب:\n{url}/vnc.html?password=123456")
            else:
                print("\n❌ لم يتم العثور على الرابط في الملف")
        else:
            print("❌ ملف cloudflared.log غير موجود")
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {str(e)}")
    
    # تقرير النهائي
    print("\n" + "=" * 60)
    print("📊 تقرير التشغيل النهائي")
    print("=" * 60)
    
    # فحص العمليات الجارية
    print("\n🔍 العمليات الجارية:")
    run_command("ps aux | grep -E '(Xvfb|firefox|cloudflared|websockify)' | grep -v grep || echo 'لا توجد عمليات'", "فحص العمليات")
    
    # فحص المنافذ المفتوحة
    print("\n🌐 المنافذ المفتوحة:")
    run_command("netstat -tuln 2>/dev/null | grep -E ':(5900|6080|8080)' || echo 'لا توجد منافذ مفتوحة'", "فحص المنافذ")
    
    # فحص الملفات المُنشأة
    print("\n📁 الملفات المُنشأة:")
    files_to_check = ["noVNC", "cloudflared", "cloudflared.log", "~/.vnc"]
    for file_path in files_to_check:
        expanded_path = os.path.expanduser(file_path)
        if os.path.exists(expanded_path):
            print(f"✅ {file_path} موجود")
        else:
            print(f"❌ {file_path} غير موجود")
    
    print("\n🎯 تم تشغيل جميع أجزاء الكود بأقصى ما يمكن في بيئة Replit")
    print("ملاحظة: بعض الأوامر قد تفشل بسبب قيود بيئة Replit على تثبيت حزم النظام")

if __name__ == "__main__":
    main()