#!/bin/bash

echo "==== تشغيل ملفات مجلد tool كما هي - $(date) ===="

# ✅ التأكد من وجود مجلد X11 الوهمي لتفادي خطأ euid != 0
echo "📁 [1/12] إنشاء /tmp/.X11-unix ..."
mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix 2>/dev/null || true

# ✅ التأكد من وجود أمر nc (netcat) 
echo "🛠️ [2/12] التأكد من وجود أمر nc ..."
command -v nc >/dev/null 2>&1 || alias nc=netcat

# 🖥️ تشغيل الشاشة الوهمية
echo "🖥️ [3/12] تشغيل Xvfb ..."
Xvfb :1 -screen 0 1024x768x16 &
export DISPLAY=:1
sleep 2

# ⚙️ محاولة تشغيل سطح المكتب البديل (fluxbox بدلاً من LXDE)
echo "🧠 [4/12] تشغيل نافذة افتراضية ..."
# بدلاً من LXDE نستخدم xterm كنافذة أساسية
xterm &
sleep 2

# 🌐 [4.5/12] محاولة تشغيل Firefox (إذا كان متاحاً)
echo "🌐 [4.5/12] البحث عن Firefox ..."
if command -v firefox >/dev/null 2>&1; then
    echo "تم العثور على Firefox، جاري التشغيل..."
    DISPLAY=:1 firefox --no-sandbox &
else
    echo "Firefox غير متاح، تخطي..."
fi
sleep 2

# 🔐 تشغيل x11vnc
echo "🔐 [5/12] تشغيل x11vnc ..."
mkdir -p ~/.vnc
echo "123456" | x11vnc -storepasswd /dev/stdin ~/.vnc/passwd
x11vnc -display :1 -rfbauth ~/.vnc/passwd -forever -shared -rfbport 5900 > /tmp/x11vnc.log 2>&1 &
sleep 2

# 🌐 تشغيل websockify (جسر VNC إلى WebSocket)
echo "🌐 [6/12] تشغيل websockify ..."
cd noVNC && python3 utils/websockify/websockify.py --web . --wrap-mode=ignore 6080 localhost:5900 > /tmp/novnc.log 2>&1 &
cd ..
sleep 2

# 🌍 تشغيل خادم HTTP على المنفذ 8080 (اختياري/احتياطي فقط)
echo "🌍 [7/12] تشغيل خادم HTTP على المنفذ 8080 ..."
cd noVNC && python3 -m http.server 8080 > /tmp/http.log 2>&1 &
cd ..
sleep 2

# ✅ التحقق من تشغيل noVNC (websockify)
echo "🧪 [8/12] التحقق من تشغيل noVNC على المنفذ 6080 ..."
if nc -z localhost 6080; then
    echo "✅ noVNC يعمل على المنفذ 6080"
else
    echo "❌ noVNC لا يعمل! عرض السجل:"
    cat /tmp/novnc.log 2>/dev/null || echo "لا يوجد سجل"
    echo "--- سجل x11vnc ---"
    cat /tmp/x11vnc.log 2>/dev/null || echo "لا يوجد سجل"
fi

# ☁️ تشغيل cloudflared على منفذ 6080 لتوفير WebSocket
echo "☁️ [9/12] تشغيل cloudflared ..."
./cloudflared tunnel --url http://localhost:6080 --no-autoupdate > /tmp/cloudflared.log 2>&1 &
sleep 10

# 🌐 طباعة رابط Cloudflare
echo "🔗 [10/12] استخراج رابط Cloudflare ..."
CLOUDFLARE_URL=$(grep -o 'https://[-a-z0-9]*\.trycloudflare\.com' /tmp/cloudflared.log | head -n 1)

if [[ -n "$CLOUDFLARE_URL" ]]; then
    echo "📡 رابط سطح المكتب عبر Cloudflare:"
    echo "$CLOUDFLARE_URL"
    echo ""
    echo "🖥️ رابط vnc.html الجاهز (انسخه وافتحه في المتصفح):"
    echo "$CLOUDFLARE_URL/vnc.html?password=123456"
    
    # حفظ الرابط في ملف
    echo "$CLOUDFLARE_URL/vnc.html?password=123456" > desktop_link.txt
    echo "💾 تم حفظ الرابط في desktop_link.txt"
else
    echo "❌ لم يتم العثور على الرابط، عرض سجل cloudflared:"
    cat /tmp/cloudflared.log 2>/dev/null || echo "لا يوجد سجل"
fi

# عرض حالة العمليات
echo "📊 [11/12] حالة العمليات:"
ps aux | grep -E "(Xvfb|x11vnc|websockify|cloudflared)" | grep -v grep

# 🔁 إبقاء السكربت يعمل
echo "🔁 [12/12] إبقاء السكربت يعمل ..."
echo "✅ تم تشغيل جميع الخدمات!"
echo "🌐 للوصول لسطح المكتب، استخدم الرابط أعلاه"
echo "⏹️ لإيقاف الخدمات: Ctrl+C"

# إبقاء السكربت نشطاً
while true; do
    sleep 60
    echo "$(date): الخدمات تعمل..."
done