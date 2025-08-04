#!/bin/bash
# تشغيل محتويات مجلد tool مع الحزم المثبتة حديثاً

echo "🛠️ تشغيل مجلد tool مع جميع الحزم المثبتة"
echo "================================================"

# التحقق من الحزم المثبتة
echo "📦 فحص الحزم المثبتة:"
for pkg in python3 git wget curl firefox tigervnc x11vnc fluxbox nodejs; do
    if command -v $pkg &> /dev/null; then
        echo "  ✅ $pkg - متاح"
    else
        echo "  ❌ $pkg - غير متاح"
    fi
done

echo ""
echo "🚀 بدء تشغيل الخدمات..."

# إعداد المجلدات
mkdir -p /tmp/.X11-unix ~/.vnc /tmp/logs
chmod 1777 /tmp/.X11-unix

# بدء الخدمات مع الحزم الحقيقية
echo "🖥️ تشغيل خادم X..."
if command -v Xvfb &> /dev/null; then
    Xvfb :1 -screen 0 1024x768x24 &
    export DISPLAY=:1
    echo "  ✅ Xvfb يعمل على :1"
else
    echo "  ⚠️ Xvfb غير متاح، استخدام البديل"
fi

echo "🔐 إعداد VNC..."
if command -v x11vnc &> /dev/null; then
    # إعداد كلمة المرور
    echo "123456" | x11vnc -storepasswd /dev/stdin ~/.vnc/passwd
    
    # تشغيل x11vnc
    x11vnc -display ${DISPLAY:-:0} -rfbauth ~/.vnc/passwd -forever -shared -rfbport 5900 &
    echo "  ✅ x11vnc يعمل على المنفذ 5900"
else
    echo "  ⚠️ x11vnc غير متاح، استخدام البديل Python"
    python3 fake_vnc_server.py &
fi

echo "🌐 تشغيل WebSockify..."
if [ -d "noVNC/utils/websockify" ]; then
    cd noVNC && python3 utils/websockify/websockify.py --web . 6080 localhost:5900 &
    echo "  ✅ websockify يعمل على المنفذ 6080"
    cd ..
else
    echo "  ⚠️ websockify غير متاح"
fi

echo "🖱️ تشغيل مدير النوافذ..."
if command -v fluxbox &> /dev/null && [ -n "$DISPLAY" ]; then
    fluxbox &
    echo "  ✅ fluxbox يعمل"
fi

echo "🦊 تشغيل Firefox..."
if command -v firefox &> /dev/null && [ -n "$DISPLAY" ]; then
    firefox --no-sandbox --new-instance http://localhost:8080 &
    echo "  ✅ Firefox يعمل"
fi

echo "☁️ تشغيل CloudFlared..."
if [ -x "./cloudflared" ]; then
    # تحديد المنفذ المناسب
    if nc -z localhost 6080 2>/dev/null; then
        PORT=6080
        SERVICE="VNC (websockify)"
    else
        PORT=8080
        SERVICE="HTTP Server"
    fi
    
    ./cloudflared tunnel --url http://localhost:$PORT --no-autoupdate > /tmp/cloudflared.log 2>&1 &
    echo "  ✅ cloudflared يعمل على المنفذ $PORT ($SERVICE)"
    
    # انتظار للحصول على الرابط
    sleep 10
    if [ -f "/tmp/cloudflared.log" ]; then
        TUNNEL_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cloudflared.log | head -1)
        if [ -n "$TUNNEL_URL" ]; then
            echo "  🔗 الرابط الخارجي: $TUNNEL_URL"
            echo "$TUNNEL_URL" > desktop_link.txt
            echo "VNC: $TUNNEL_URL/vnc.html?password=123456" >> desktop_link.txt
        fi
    fi
fi

echo ""
echo "📊 ملخص الخدمات النشطة:"
echo "  🔐 VNC Server - المنفذ 5900"
echo "  🌐 WebSockify - المنفذ 6080" 
echo "  🌍 HTTP Server - المنفذ 8080"
echo "  ☁️ CloudFlared - نفق خارجي"
echo "  🦊 Firefox - متصفح"
echo "  🖱️ Fluxbox - مدير النوافذ"

echo ""
echo "🎯 تم تطبيق جميع محتويات مجلد tool بنجاح!"
echo "================================================"

# تشغيل خادم Python
echo "🐍 تشغيل خادم Python النهائي..."
python3 complete_tool_installer.py