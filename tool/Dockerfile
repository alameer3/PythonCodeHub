# 🌐 قاعدة Ubuntu
FROM ubuntu:22.04

# ✅ تجاوز الإعداد التفاعلي + تثبيت tzdata وتحديد المنطقة الزمنية
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Riyadh /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# 🛠️ تثبيت الأدوات الأساسية وسطح المكتب و VNC و noVNC و Firefox
RUN apt update && apt install -y \
    lxde \
    x11vnc \
    xvfb \
    git \
    wget \
    python3 \
    python3-pip \
    firefox \
    curl \
    net-tools \
    netcat \
    # ✅ تم حذف novnc لمنع تعارض المسارات (سيتم تثبيته من git أدناه)
    tzdata \
    && apt clean

# 🦊 تثبيت Firefox يدويًا بدون Snap
RUN apt remove -y firefox || true && \
    wget -O /tmp/firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=ar" && \
    tar -xjf /tmp/firefox.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox

# 🔐 إعداد كلمة مرور VNC
RUN mkdir -p /root/.vnc && \
    x11vnc -storepasswd 123456 /root/.vnc/passwd

# 🌀 تحميل noVNC و websockify
RUN rm -rf /opt/noVNC && \
    git clone --branch v1.2.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    chmod +x /opt/noVNC/utils/launch.sh

# 🌐 تحميل cloudflared
RUN wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /usr/local/bin/cloudflared && \
    chmod +x /usr/local/bin/cloudflared

# ⏱️ تعيين التوقيت يدويًا لتجنب التفاعل
RUN ln -sf /usr/share/zoneinfo/Asia/Riyadh /etc/localtime && \
    echo "Asia/Riyadh" > /etc/timezone && \
    DEBIAN_FRONTEND=noninteractive apt install -y tzdata

# ✅ إصلاح صلاحيات مجلد X11 لتجنب تحذير Xvfb
RUN mkdir -p /tmp/.X11-unix && \
    chown root:root /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# 🖥️ نسخ سكربت التشغيل
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

# ✅ إعداد autostart لتشغيل Firefox تلقائيًا مع سطح المكتب (داخل جلسة LXDE)
RUN mkdir -p /root/.config/lxsession/LXDE && \
    echo "@firefox --no-sandbox --setDefaultBrowser" >> /root/.config/lxsession/LXDE/autostart && \
    echo "@lxterminal" >> /root/.config/lxsession/LXDE/autostart

# 🔥 بدء التشغيل
CMD ["/start.sh"]