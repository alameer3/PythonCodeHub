#!/usr/bin/env python3
# سطح مكتب بسيط يعمل 100% في Replit
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import subprocess
import os
from datetime import datetime

class DesktopHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_desktop()
        elif self.path == '/run':
            self.run_python()
        else:
            super().do_GET()
    
    def send_desktop(self):
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>سطح المكتب - يعمل بالفعل!</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(45deg, #667eea, #764ba2); 
               color: white; padding: 20px; min-height: 100vh; }}
        .window {{ background: rgba(255,255,255,0.1); padding: 20px; margin: 10px 0; 
                  border-radius: 15px; backdrop-filter: blur(10px); }}
        .app {{ background: rgba(255,255,255,0.2); padding: 15px; margin: 10px; 
               border-radius: 10px; cursor: pointer; display: inline-block; }}
        .app:hover {{ background: rgba(255,255,255,0.3); }}
        button {{ background: #4CAF50; color: white; border: none; padding: 10px 20px; 
                 border-radius: 5px; cursor: pointer; margin: 5px; }}
        #output {{ background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; 
                  font-family: monospace; white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="window">
        <h1>🖥️ سطح المكتب التفاعلي</h1>
        <p><strong style="color: #4CAF50;">✅ هذا التطبيق يعمل 100% في Replit!</strong></p>
        <p>الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="window">
        <h2>📱 التطبيقات</h2>
        <div class="app" onclick="runPython()">🐍 تشغيل Python</div>
        <div class="app" onclick="showInfo()">💻 معلومات النظام</div>
        <div class="app" onclick="showTime()">⏰ الوقت</div>
        <div class="app" onclick="calculate()">🧮 حاسبة</div>
    </div>

    <div class="window">
        <h2>📋 النتائج</h2>
        <div id="output">انقر على أي تطبيق أعلاه لرؤية النتائج هنا...</div>
        <button onclick="clearOutput()">مسح</button>
    </div>

    <script>
        function showOutput(text) {{
            document.getElementById('output').textContent = '[' + new Date().toLocaleTimeString() + '] ' + text;
        }}
        
        function runPython() {{
            showOutput('جاري تشغيل Python...');
            fetch('/run').then(r => r.text()).then(data => {{
                showOutput('نتيجة Python:\\n' + data);
            }}).catch(() => showOutput('خطأ في تشغيل Python'));
        }}
        
        function showInfo() {{
            const info = 'معلومات النظام:\\n' +
                        'المتصفح: ' + navigator.userAgent.split(' ')[0] + '\\n' +
                        'الوقت: ' + new Date().toLocaleString('ar') + '\\n' +
                        'العرض: ' + screen.width + 'x' + screen.height;
            showOutput(info);
        }}
        
        function showTime() {{
            showOutput('الوقت الحالي: ' + new Date().toLocaleString('ar'));
        }}
        
        function calculate() {{
            const num1 = prompt('ادخل الرقم الأول:') || '0';
            const num2 = prompt('ادخل الرقم الثاني:') || '0';
            const result = parseFloat(num1) + parseFloat(num2);
            showOutput(`حاسبة: ${{num1}} + ${{num2}} = ${{result}}`);
        }}
        
        function clearOutput() {{
            document.getElementById('output').textContent = 'تم مسح النتائج...';
        }}
        
        // رسالة ترحيب
        setTimeout(() => showOutput('🎉 مرحباً! جميع الوظائف جاهزة للاستخدام'), 1000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def run_python(self):
        try:
            result = subprocess.run(['python3', 'my_code.py'], 
                                  capture_output=True, text=True, timeout=10)
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')  
            self.end_headers()
            self.wfile.write(result.stdout.encode('utf-8'))
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f'خطأ: {str(e)}'.encode('utf-8'))

print("🚀 تشغيل سطح المكتب البسيط على المنفذ 5000")
server = HTTPServer(('0.0.0.0', 5000), DesktopHandler)
server.serve_forever()