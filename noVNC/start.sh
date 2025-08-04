#!/bin/bash

export DISPLAY=:0

# ✅ تثبيت Xvfb وLXDE تلقائيًا إن لم تكن مثبتة (مرة واحدة فقط)
if ! command -v Xvfb >/dev/null; then
    echo "⏳ جاري التثبيت الأولي للأدوات..."
    sudo apt update
    sudo apt install -y xvfb lxde x11vnc chromium-browser net-tools netcat curl git wget python3 unzip
fi

# 🖥️ تشغيل الشاشة الوهمية
Xvfb :0 -screen 0 1024x768x16 &
sleep 2

# ⚙️ تشغيل LXDE
startlxde > lxde.log 2>&1 &
sleep 2

# 🌐 تشغيل Chromium
chromium-browser --no-sandbox > chrome.log 2>&1 &
sleep 2

# 🔐 تشغيل x11vnc
mkdir -p ~/.vnc
x11vnc -display :0 -passwd 123456 -forever -shared > x11vnc.log 2>&1 &
sleep 2

# 📥 تحميل noVNC داخل مجلد آمن
NOVNC_DIR="$HOME/novnc"
if [ ! -d "$NOVNC_DIR/noVNC" ]; then
    git clone https://github.com/novnc/noVNC.git "$NOVNC_DIR/noVNC"
    git clone https://github.com/novnc/websockify "$NOVNC_DIR/noVNC/utils/websockify"
fi

# 🌐 تشغيل noVNC
"$NOVNC_DIR/noVNC/utils/launch.sh" --vnc localhost:5900 &
sleep 3

# ☁️ تحميل وتشغيل cloudflared
if [ ! -f "$NOVNC_DIR/cloudflared" ]; then
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O "$NOVNC_DIR/cloudflared"
    chmod +x "$NOVNC_DIR/cloudflared"
fi

"$NOVNC_DIR/cloudflared" tunnel --url http://localhost:6080 --no-autoupdate > link.log 2>&1 &
sleep 10

echo "🔗 رابط سطح المكتب:"
grep -o 'https://.*\.trycloudflare.com' link.log | head -n1