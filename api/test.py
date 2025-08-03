from http.server import BaseHTTPRequestHandler
import os
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/':
            response = {"message": "API は動作しています!"}
        elif self.path == '/test':
            response = {"test": "success"}
        elif self.path == '/env':
            response = {
                "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET"),
                "supabase_key": os.environ.get("SUPABASE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_KEY") else "NOT_SET",
                "supabase_service_key": os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_SERVICE_KEY") else "NOT_SET",
                "debug": os.environ.get("DEBUG", "NOT_SET"),
                "status": "success"
            }
        elif self.path == '/basic':
            response = {
                "message": "Basic endpoint works",
                "timestamp": "2024-01-01",
                "status": "ok"
            }
        elif self.path == '/os-test':
            response = {
                "platform": os.name,
                "cwd": os.getcwd(),
                "status": "os_info"
            }
        else:
            response = {"error": "Not found", "path": self.path}
        
        self.wfile.write(json.dumps(response).encode())
        return 