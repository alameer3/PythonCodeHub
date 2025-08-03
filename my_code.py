#!/usr/bin/env python3
"""
ملف الكود الخاص بك - يمكنك كتابة أي كود تريده هنا
Your Custom Code File - Write any code you want here
"""

# يمكنك استيراد أي مكتبات تحتاجها
# You can import any libraries you need
import os
import sys
from datetime import datetime

# إضافة مسار المشروع للاستفادة من الوحدات الموجودة
# Add project path to use existing modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# يمكنك استيراد الوحدات من المشروع الموجود (إذا احتجتها)
# You can import modules from the existing project (if needed)
# من أجل البساطة، سنكتب دوال بسيطة بدلاً من الاستيراد
# For simplicity, we'll write simple functions instead of importing

def validate_email_simple(email):
    """تحقق بسيط من صحة البريد الإلكتروني"""
    return "@" in email and "." in email

def format_time_simple(seconds):
    """تنسيق بسيط للوقت"""
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        return f"{seconds//60} دقيقة"
    else:
        return f"{seconds//3600} ساعة"


def main():
    """الدالة الرئيسية - ضع كودك هنا"""
    print("🚀 مرحباً! هذا ملف الكود الخاص بك")
    print("=" * 50)
    
    # مثال على استخدام الدوال البسيطة
    print("\n📧 اختبار التحقق من البريد الإلكتروني:")
    email = "test@example.com"
    is_valid = validate_email_simple(email)
    print(f"البريد: {email} - {'صحيح' if is_valid else 'غير صحيح'}")
    
    print("\n⏱️ اختبار تنسيق الوقت:")
    duration = 3661  # ثانية
    formatted = format_time_simple(duration)
    print(f"{duration} ثانية = {formatted}")
    
    print("\n🆔 إنشاء معرف بسيط:")
    import random
    unique_id = f"USER_{random.randint(1000, 9999)}"
    print(f"المعرف الجديد: {unique_id}")
    
    print("\n📅 الوقت الحالي:")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"الوقت: {current_time}")
    
    # يمكنك إضافة كودك الخاص هنا
    print("\n" + "="*50)
    print("💻 ضع كودك الخاص تحت هذا السطر:")
    print("="*50)
    
    # ========== منطقة الكود الخاص بك ==========
    # اكتب كودك هنا...
    
    # مثال بسيط:
    print("مثال على كود بسيط:")
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"مجموع الأرقام {numbers} = {total}")
    
    # مثال على استخدام حلقة
    print("\nطباعة الأرقام من 1 إلى 5:")
    for i in range(1, 6):
        print(f"الرقم: {i}")
    
    # مثال على استخدام دالة
    def greet(name):
        return f"مرحباً {name}!"
    
    print(f"\n{greet('المطور')}")
    
    # ========== نهاية منطقة الكود الخاص بك ==========
    
    print("\n✅ تم تشغيل الكود بنجاح!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        sys.exit(1)