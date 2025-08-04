#!/usr/bin/env python3
"""
مشغل Chrome المحسن لبيئة tool
"""

import subprocess
import os
import time

def launch_chrome():
    """تشغيل Chrome مع إعدادات محسنة"""
    print("🌐 تشغيل Google Chrome...")
    
    # التحقق من توفر Chrome/Chromium
    chrome_commands = ['chromium', 'chromium-browser', 'google-chrome', 'chrome']
    chrome_cmd = None
    
    for cmd in chrome_commands:
        if subprocess.run(f"command -v {cmd}", shell=True, capture_output=True).returncode == 0:
            chrome_cmd = cmd
            print(f"  ✅ تم العثور على {cmd}")
            break
    
    if not chrome_cmd:
        print("  ❌ Chrome/Chromium غير متاح")
        return False
    
    # إعدادات Chrome المحسنة
    chrome_args = [
        chrome_cmd,
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-software-rasterizer',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-extensions',
        '--no-first-run',
        '--no-default-browser-check',
        '--window-size=1024,768',
        'http://localhost:8080'
    ]
    
    try:
        # تشغيل Chrome
        process = subprocess.Popen(chrome_args, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("  ✅ Chrome يعمل بنجاح")
            return process
        else:
            print("  ❌ فشل في تشغيل Chrome")
            return False
            
    except Exception as e:
        print(f"  ❌ خطأ في تشغيل Chrome: {str(e)}")
        return False

if __name__ == "__main__":
    launch_chrome()