#!/usr/bin/env python3
import socket
import threading
import time

class FakeVNCServer:
    def __init__(self, port=5900):
        self.port = port
        self.running = False
        
    def start(self):
        self.running = True
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', self.port))
                s.listen(5)
                print(f"VNC Server listening on port {self.port}")
                
                while self.running:
                    try:
                        conn, addr = s.accept()
                        with conn:
                            # رد بسيط لمحاكاة VNC
                            conn.send(b"RFB 003.008\n")
                            time.sleep(0.1)
                    except:
                        break
        except Exception as e:
            print(f"VNC Server error: {e}")

if __name__ == "__main__":
    server = FakeVNCServer()
    server.start()
