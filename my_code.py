# ملف الكود الخاص بك - مثال تطبيقي متطور
import os
import json
import time
from datetime import datetime
import requests

def main():
    """دالة رئيسية لتشغيل التطبيق"""
    print("🚀 مرحباً بك في التطبيق المتطور!")
    print("=" * 50)
    
    # عرض معلومات النظام
    show_system_info()
    
    # تشغيل عمليات مختلفة
    run_calculations()
    run_data_processing()
    run_api_example()
    
    print("\n✅ تم تشغيل جميع العمليات بنجاح!")

def show_system_info():
    """عرض معلومات النظام"""
    print("\n📊 معلومات النظام:")
    print(f"  الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  مجلد العمل: {os.getcwd()}")
    print(f"  متغيرات البيئة المهمة:")
    for key in ['PATH', 'HOME', 'USER']:
        value = os.environ.get(key, 'غير محدد')
        print(f"    {key}: {value[:50]}..." if len(str(value)) > 50 else f"    {key}: {value}")

def run_calculations():
    """تشغيل عمليات حسابية متقدمة"""
    print("\n🧮 العمليات الحسابية:")
    
    # حساب القوى
    numbers = [2, 3, 5, 7, 10]
    for num in numbers:
        square = num ** 2
        cube = num ** 3
        print(f"  العدد {num}: المربع = {square}, المكعب = {cube}")
    
    # حساب المتوسط
    average = sum(numbers) / len(numbers)
    print(f"  المتوسط: {average:.2f}")

def run_data_processing():
    """معالجة البيانات"""
    print("\n📁 معالجة البيانات:")
    
    # إنشاء بيانات تجريبية
    data = {
        "المشروع": "تطبيق بايثون متطور",
        "التاريخ": datetime.now().isoformat(),
        "البيانات": [
            {"الاسم": "أحمد", "العمر": 25, "المدينة": "الرياض"},
            {"الاسم": "فاطمة", "العمر": 30, "المدينة": "جدة"},
            {"الاسم": "محمد", "العمر": 28, "المدينة": "الدمام"}
        ]
    }
    
    # حفظ البيانات في ملف
    filename = "data_output.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ تم حفظ البيانات في ملف: {filename}")
    print(f"  📊 عدد السجلات: {len(data['البيانات'])}")

def run_api_example():
    """مثال على استخدام API"""
    print("\n🌐 مثال API:")
    
    try:
        # مثال على طلب HTTP بسيط
        response = requests.get("https://httpbin.org/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ تم الاتصال بـ API بنجاح")
            print(f"  📋 البيانات المستلمة: {json.dumps(data, indent=2)[:100]}...")
        else:
            print(f"  ❌ خطأ في الاتصال: {response.status_code}")
    except requests.RequestException as e:
        print(f"  ❌ خطأ في الشبكة: {str(e)}")

if __name__ == "__main__":
    main()