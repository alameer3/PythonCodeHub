import socket
import threading
import time

class SimpleVNCServer:
    def __init__(self, port=5900):
        self.port = port
        self.running = True
        
    def handle_client(self, conn, addr):
        try:
            # رد VNC بسيط
            conn.send(b"RFB 003.008\n")
            data = conn.recv(1024)
            if data:
                conn.send(b"\x01")  # Security result: OK
            while self.running:
                time.sleep(1)
        except:
            pass
        finally:
            conn.close()
            
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('localhost', self.port))
            s.listen(5)
            print(f"VNC Server على المنفذ {self.port}")
            
            while self.running:
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=self.handle_client, 
                                   args=(conn, addr), daemon=True).start()
                except:
                    break

if __name__ == "__main__":
    server = SimpleVNCServer()
    server.start()