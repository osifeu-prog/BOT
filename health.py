"""
🏥 Health check endpoint for Railway
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # נתיב ברירת מחדל
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics':
            # endpoint פשוט למדידות
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'# NFTY ULTRA CASINO Metrics\n\n')
            self.wfile.write(b'app_healthy 1\n')
            self.wfile.write(b'app_ready 1\n')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # כבה לוגים של health check
        pass

def run_health_server():
    """הרץ שרת health check"""
    port = int(os.environ.get("PORT", 8080))
    
    # ודא שאנחנו לא משתמשים בפורט שכבר בשימוש
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"🏥 Health check server running on port {port}")
        print(f"🌐 Endpoints: http://0.0.0.0:{port}/health")
        server.serve_forever()
    except OSError as e:
        print(f"⚠️  Health server error (port {port} might be in use): {e}")

if __name__ == '__main__':
    # הרץ בשרשור נפרד אם צריך
    run_health_server()
