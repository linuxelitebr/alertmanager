from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("Alert received:\n", json.loads(post_data))
        self.send_response(200)
        self.end_headers()

server = HTTPServer(('0.0.0.0', 9099), WebhookHandler)
print("Waiting for webhook alerts...")
server.serve_forever()