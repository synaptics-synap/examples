import json
import threading
import subprocess
import re
from websocket_server import WebsocketServer
import http.server


class WebSockets:
    def __init__(self, host="0.0.0.0", port=6789, loglevel=0, index=None):
        """
        Init the WebSocket server.
        If index is set, it also starts a simple web server on port 80 that always returns the given file.

        :param host: IP to bind the server.
        :param port: Port for the WebSocket server.
        :param loglevel: Logging level.
        :param index: Path to the file to serve on port 80.
        """
        self.host = host
        self.port = port
        self.loglevel = loglevel
        self.index_page = index
        self.server = WebsocketServer(
            host=self.host, port=self.port, loglevel=self.loglevel
        )
        self.connected_clients = []
        self.clients_lock = threading.Lock()
        self.thread = None
        self.is_running = False
        self.httpd = None
        self.web_server_thread = None

        # Set callback functions
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)

    def new_client(self, client, server):
        """
        Called when a new WebSocket client connects.
        """
        with self.clients_lock:
            self.connected_clients.append(client)
        print(f"WebSocket client connected: {client['address']}")

    def client_left(self, client, server):
        """
        Called when a WebSocket client disconnects.
        """
        with self.clients_lock:
            if client in self.connected_clients:
                self.connected_clients.remove(client)
        print(f"WebSocket client disconnected: {client['address']}")

    def make_handler(self, index_path):
        """
        Build a simple HTTP handler that serves the file at index_path regardless of the GET request.
        """

        class CustomHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    with open(index_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except Exception as e:
                    self.send_error(404, "File not found")

            def log_message(self, format, *args):
                # Disable default logging.
                return

        return CustomHandler

    def start(self):
        """
        Start the WebSocket server in a new thread.
        If index_page is set, also start the web server on port 80.
        """
        if not self.is_running:
            ip = self.get_eth0_ip()
            print(f"Starting WebSocket server on port {self.port}")
            self.thread = threading.Thread(target=self.server.run_forever, daemon=True)
            self.thread.start()
            self.is_running = True
            print("WebSocket server started.")
            # Yellow terminal message

            if self.index_page:
                handler = self.make_handler(self.index_page)
                try:
                    self.httpd = http.server.HTTPServer((self.host, 80), handler)
                    self.web_server_thread = threading.Thread(
                        target=self.httpd.serve_forever, daemon=True
                    )
                    self.web_server_thread.start()
                    print(f"\033[93mOpen your web browser at http://{ip}\033[0m")
                except Exception as e:
                    print(f"Failed to start web server on port 80: {e}")
        else:
            print("WebSocket server is already running.")

    def shutdown(self):
        """
        Shut down the WebSocket server and the web server if running.
        """
        if self.is_running:
            print("Shutting down WebSocket server...")
            self.server.shutdown()
            self.thread.join()
            if self.index_page and self.httpd:
                print("Shutting down web server...")
                self.httpd.shutdown()
                self.web_server_thread.join()
            self.is_running = False
            print("WebSocket server has been shut down.")
        else:
            print("WebSocket server is not running.")

    def broadcast(self, message):
        """
        Send a message to all connected WebSocket clients.

        :param message: The message to send (should be a JSON string).
        """
        with self.clients_lock:
            for client in self.connected_clients.copy():
                try:
                    self.server.send_message(client, message)
                except Exception as e:
                    print(f"Error sending message to {client['address']}: {e}")

    def get_eth0_ip(self):
        ip = None
        try:
            output = subprocess.check_output(["ifconfig", "eth0"]).decode("utf-8")
            match = re.search(r"inet addr:(\S+)", output)
            if match:
                ip = match.group(1)
        except subprocess.CalledProcessError:
            pass

        if not ip:
            try:
                output = subprocess.check_output(["ifconfig", "wlan0"]).decode("utf-8")
                match = re.search(r"inet addr:(\S+)", output)
                if match:
                    ip = match.group(1)
            except subprocess.CalledProcessError:
                pass

        return ip
