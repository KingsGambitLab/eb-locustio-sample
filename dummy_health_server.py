import http.server
import socketserver
import os
import signal
import atexit

# Elastic Beanstalk will set the PORT environment variable for the web process
PORT = int(os.environ.get("PORT", 8080)) # Default to 8080 if PORT isn't set, though EB should set it
# PID_FILE logic removed - systemd will handle this if configured via option_settings

class SimpleHealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Adjusted health check path to be just "/" for Procfile web common practice
        # EB Health check can be configured to hit "/" or a specific path like "/health"
        if self.path == "/health" or self.path == "/": 
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    # Signal handling for graceful shutdown
    def signal_handler(signum, frame):
        print(f"Dummy health server (Procfile): Signal {signum} received, shutting down.")
        if 'httpd' in locals() or 'httpd' in globals():
            httpd.server_close() # Close the server socket
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Bind to 0.0.0.0 to be accessible
    with socketserver.TCPServer(("0.0.0.0", PORT), SimpleHealthHandler) as httpd:
        current_pid = os.getpid() # Get PID for logging, not for file creation
        print(f"Dummy health server (Procfile) serving on port {PORT}, PID {current_pid}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Dummy health server (Procfile): Keyboard interrupt received, shutting down.")
        finally:
            # Ensure server is closed on any exit
            if 'httpd' in locals() or 'httpd' in globals():
                httpd.server_close() 