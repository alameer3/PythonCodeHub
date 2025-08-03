# ملف الكود الخاص بك
import os
import time
import requests

# تثبيت الحزم عبر بايثون
os.system("apt update -y")
os.system("apt install -y firefox x11vnc xvfb lxde novnc websockify wget")

# إعداد كلمة مرور VNC
os.system("mkdir -p ~/.vnc")
os.system("x11vnc -storepasswd 123456 ~/.vnc/passwd")

# تشغيل الشاشة الوهمية وسطح المكتب وفايرفوكس
os.system("Xvfb :1 -screen 0 1024x768x16 &")
os.environ["DISPLAY"] = ":1"
os.system("startlxde &")
os.system("firefox &")

# تحميل Cloudflared وتشغيله
os.system("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared")
os.system("chmod +x cloudflared")
os.system("./cloudflared tunnel --url http://localhost:6080/ --no-autoupdate &")

# تشغيل noVNC
os.system("websockify --web=/usr/share/novnc/ 6080 localhost:5900 &")

# الانتظار وجلب رابط cloudflared
time.sleep(15)
try:
    r = requests.get("http://localhost:4040/api/tunnels")
    url = r.json()['tunnels'][0]['public_url']
    print("✅ رابط سطح المكتب:", url + "/vnc.html?password=123456")
except:
    print("❌ لم يتم الحصول على الرابط. حاول لاحقاً.")
print("مرحباً! ضع كودك في هذا الملف")

# مثال على حساب القوى إذا كنت تقصد ذلك
number = 5
square = number ** 2
print(f"{number} مرفوع للقوة الثانية = {square}")