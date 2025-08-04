
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import subprocess
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/run-python':
            try:
                result = subprocess.run(['python3', 'my_code.py'], 
                                      capture_output=True, text=True)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result.stdout.encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {"status": "active", "time": "now"}
            self.wfile.write(json.dumps(status).encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8080), CustomHandler)
    print("🌐 خادم الويب يعمل على المنفذ 8080")
    server.serve_forever()
