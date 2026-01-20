# Health check endpoint for Railway
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Disable logging

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("Health check server running on port 8080")
    server.serve_forever()

if __name__ == '__main__':
    # Run in a separate thread if needed
    run_health_server()
