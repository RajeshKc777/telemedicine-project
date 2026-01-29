import os
import ssl
import django
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn
import socket

class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
    pass

def run_https_server():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telemedicine.settings')
    django.setup()
    
    application = get_wsgi_application()
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('sslcert/cert.pem', 'sslcert/key.pem')
    
    # Create server
    server = make_server('0.0.0.0', 8000, application, 
                        server_class=ThreadedWSGIServer)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print("Starting HTTPS server on https://0.0.0.0:8000")
    print("Access via:")
    print("  https://localhost:8000")
    print("  https://127.0.0.1:8000")
    print("  https://192.168.1.71:8000")
    print("\nPress Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == '__main__':
    run_https_server()