#!/usr/bin/env python3
"""Simple HTTP server to serve the frontend"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "public"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🌐 CourseSpider Frontend Server")
        print("=" * 60)
        print(f"📡 Server running on: http://localhost:{PORT}")
        print(f"📂 Serving files from: {DIRECTORY}/")
        print("")
        print("Available pages:")
        print(f"  • Home:   http://localhost:{PORT}/index.html")
        print(f"  • Browse: http://localhost:{PORT}/browse.html")
        print("")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        httpd.serve_forever()
