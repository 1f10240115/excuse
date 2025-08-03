from http.server import BaseHTTPRequestHandler
import os
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "supabase_url": os.environ.get("SUPABASE_URL", "NOT_SET"),
            "supabase_key": os.environ.get("SUPABASE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_KEY") else "NOT_SET",
            "supabase_service_key": os.environ.get("SUPABASE_SERVICE_KEY", "NOT_SET")[:10] + "..." if os.environ.get("SUPABASE_SERVICE_KEY") else "NOT_SET",
            "debug": os.environ.get("DEBUG", "NOT_SET"),
            "status": "success"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return 