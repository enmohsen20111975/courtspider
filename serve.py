#!/usr/bin/env python3
"""
Simple HTTP server for standalone app
Serves files from current directory on port 8080
"""

import http.server
import socketserver
import os

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for database file
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("\n" + "="*60)
        print("📚 Standalone Course Viewer Server")
        print("="*60)
        print(f"🌐 Server running at: http://localhost:{PORT}")
        print(f"📂 Serving from: {os.getcwd()}")
        print("\nOpen in browser: http://localhost:8080/index.html")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
