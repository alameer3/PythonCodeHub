#!/usr/bin/env python3
import os
import json
import subprocess
from datetime import datetime

def show_desktop_menu():
    """عرض قائمة سطح المكتب التفاعلية"""
    print("\n" + "="*60)
    print("🖥️  سطح المكتب التفاعلي - يعمل بالفعل في Replit!")
    print("="*60)
    print("📅 الوقت:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("📁 المجلد:", os.getcwd())
    print("👤 المستخدم:", os.environ.get('USER', 'runner'))
    print("\n📱 التطبيقات المتاحة:")
    print("  1️⃣  تشغيل تطبيق Python المتطور")
    print("  2️⃣  عرض معلومات النظام")
    print("  3️⃣  قائمة الملفات")
    print("  4️⃣  الآلة الحاسبة")
    print("  5️⃣  معلومات الشبكة")
    print("  6️⃣  عرض متغيرات البيئة")
    print("  7️⃣  تشغيل أوامر مخصصة")
    print("  0️⃣  خروج")
    print("="*60)

def run_python_app():
    """تشغيل تطبيق Python"""
    print("\n🐍 جاري تشغيل تطبيق Python المتطور...")
    print("-" * 50)
    try:
        result = subprocess.run(['python3', 'my_code.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ تم التشغيل بنجاح!")
            print(result.stdout)
        else:
            print("❌ حدث خطأ:")
            print(result.stderr)
    except Exception as e:
        print(f"💥 خطأ في التشغيل: {str(e)}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def show_system_info():
    """عرض معلومات النظام"""
    print("\n💻 معلومات النظام:")
    print("-" * 30)
    print(f"🕐 الوقت الحالي: {datetime.now()}")
    print(f"📂 مجلد العمل: {os.getcwd()}")
    print(f"👤 اسم المستخدم: {os.environ.get('USER', 'غير محدد')}")
    print(f"🏠 المجلد الرئيسي: {os.environ.get('HOME', 'غير محدد')}")
    
    # معلومات Python
    try:
        python_version = subprocess.check_output(['python3', '--version']).decode().strip()
        print(f"🐍 إصدار Python: {python_version}")
    except:
        print("🐍 إصدار Python: غير متاح")
    
    # معلومات الذاكرة
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.readline()
            print(f"💾 الذاكرة: {mem_info.split()[1]} KB")
    except:
        print("💾 معلومات الذاكرة: غير متاحة")
    
    input("\n📎 اضغط Enter للمتابعة...")

def list_files():
    """عرض قائمة الملفات"""
    print("\n📁 قائمة الملفات والمجلدات:")
    print("-" * 40)
    
    try:
        items = sorted(os.listdir('.'))
        for item in items[:20]:  # عرض أول 20 عنصر
            if os.path.isdir(item):
                print(f"📁 {item}/")
            else:
                size = os.path.getsize(item)
                print(f"📄 {item} ({size} bytes)")
        
        if len(items) > 20:
            print(f"\n... و {len(items) - 20} عنصر إضافي")
            
    except Exception as e:
        print(f"❌ خطأ في قراءة الملفات: {str(e)}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def calculator():
    """آلة حاسبة بسيطة"""
    print("\n🧮 الآلة الحاسبة")
    print("-" * 20)
    
    try:
        print("أدخل العملية الحسابية (مثال: 5 + 3 * 2):")
        expression = input("➤ ")
        
        if expression.strip():
            # تنظيف وتقييم التعبير بأمان
            allowed_chars = "0123456789+-*/(). "
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                print(f"النتيجة: {expression} = {result}")
            else:
                print("❌ يرجى استخدام أرقام وعلامات حسابية فقط")
        else:
            print("❌ لم تدخل أي عملية حسابية")
            
    except Exception as e:
        print(f"❌ خطأ في الحساب: {str(e)}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def network_info():
    """معلومات الشبكة"""
    print("\n🌐 معلومات الشبكة:")
    print("-" * 25)
    
    try:
        # معلومات IP
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🌍 عنوان IP: {result.stdout.strip()}")
        
        # معلومات DNS
        result = subprocess.run(['nslookup', 'google.com'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ الاتصال بالإنترنت متاح")
        else:
            print("❌ مشكلة في الاتصال بالإنترنت")
            
    except Exception as e:
        print(f"❌ خطأ في فحص الشبكة: {str(e)}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def show_env_vars():
    """عرض متغيرات البيئة المهمة"""
    print("\n🔧 متغيرات البيئة المهمة:")
    print("-" * 35)
    
    important_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'DISPLAY', 'LANG']
    
    for var in important_vars:
        value = os.environ.get(var, 'غير محدد')
        if len(value) > 60:
            value = value[:60] + "..."
        print(f"{var}: {value}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def custom_command():
    """تشغيل أوامر مخصصة"""
    print("\n💻 تشغيل أمر مخصص:")
    print("-" * 25)
    print("⚠️  تحذير: استخدم أوامر آمنة فقط")
    
    command = input("أدخل الأمر: ").strip()
    
    if command:
        # قائمة الأوامر الآمنة المسموحة
        safe_commands = ['ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free']
        
        if command.split()[0] in safe_commands:
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("✅ النتيجة:")
                    print(result.stdout)
                else:
                    print("❌ خطأ:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ خطأ في التشغيل: {str(e)}")
        else:
            print("❌ هذا الأمر غير مسموح لأسباب أمنية")
            print(f"الأوامر المسموحة: {', '.join(safe_commands)}")
    
    input("\n📎 اضغط Enter للمتابعة...")

def main():
    """الدالة الرئيسية لسطح المكتب"""
    print("🎉 مرحباً بك في سطح المكتب التفاعلي!")
    print("✅ هذا التطبيق يعمل 100% في Replit")
    
    while True:
        try:
            show_desktop_menu()
            choice = input("\n🎯 اختر رقم التطبيق: ").strip()
            
            if choice == '1':
                run_python_app()
            elif choice == '2':
                show_system_info()
            elif choice == '3':
                list_files()
            elif choice == '4':
                calculator()
            elif choice == '5':
                network_info()
            elif choice == '6':
                show_env_vars()
            elif choice == '7':
                custom_command()
            elif choice == '0':
                print("\n👋 شكراً لاستخدام سطح المكتب التفاعلي!")
                break
            else:
                print("\n❌ اختيار غير صحيح، حاول مرة أخرى")
                input("📎 اضغط Enter للمتابعة...")
                
        except KeyboardInterrupt:
            print("\n\n🔄 تم إيقاف البرنامج")
            break
        except Exception as e:
            print(f"\n💥 خطأ غير متوقع: {str(e)}")
            input("📎 اضغط Enter للمتابعة...")

if __name__ == "__main__":
    main()