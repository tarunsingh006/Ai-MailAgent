import http.server
import webbrowser

PORT = 3000

handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("", PORT), handler)

print(f"Frontend running at http://localhost:{PORT}")
webbrowser.open(f"http://localhost:{PORT}")
httpd.serve_forever()
