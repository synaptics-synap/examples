import json
import threading
import subprocess
import re
from websocket_server import WebsocketServer

class WebSockets:
    def __init__(self, host="0.0.0.0", port=6789, loglevel=0):
        """
        Initializes the WebSocket server.

        :param host: IP address to bind the server to.
        :param port: Port number for the WebSocket server.
        :param loglevel: Logging level for the server.
        """
        self.host = host
        self.port = port
        self.loglevel = loglevel
        self.server = WebsocketServer(host=self.host, port=self.port, loglevel=self.loglevel)
        self.connected_clients = []
        self.clients_lock = threading.Lock()
        self.thread = None
        self.is_running = False

        # Set callback functions
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)

    def new_client(self, client, server):
        """
        Callback when a new WebSocket client connects.
        """
        with self.clients_lock:
            self.connected_clients.append(client)
        print(f"WebSocket client connected: {client['address']}")

    def client_left(self, client, server):
        """
        Callback when a WebSocket client disconnects.
        """
        with self.clients_lock:
            if client in self.connected_clients:
                self.connected_clients.remove(client)
        print(f"WebSocket client disconnected: {client['address']}")

    def start(self):
        """
        Starts the WebSocket server in a separate thread.
        """
        if not self.is_running:
            print(f"Starting WebSocket server on {self.get_eth0_ip()}:{self.port}")
            self.thread = threading.Thread(target=self.server.run_forever, daemon=True)
            self.thread.start()
            self.is_running = True
            print("WebSocket server started.")
        else:
            print("WebSocket server is already running.")

    def shutdown(self):
        """
        Shuts down the WebSocket server gracefully.
        """
        if self.is_running:
            print("Shutting down WebSocket server...")
            self.server.shutdown()
            self.thread.join()
            self.is_running = False
            print("WebSocket server has been shut down.")
        else:
            print("WebSocket server is not running.")

    def broadcast(self, message):
        """
        Broadcasts a message to all connected WebSocket clients.

        :param message: The message to broadcast (should be a JSON string).
        """
        with self.clients_lock:
            for client in self.connected_clients.copy():
                try:
                    self.server.send_message(client, message)
                except Exception as e:
                    print(f"Error sending message to {client['address']}: {e}")

    def get_eth0_ip(self):
        try:
            # Run "ifconfig eth0" and capture its output
            output = subprocess.check_output(["ifconfig", "eth0"]).decode("utf-8")
            
            # Search for the line that includes 'inet addr:'
            # Example line: "inet addr:10.3.10.105  Bcast:10.3.11.255  Mask:255.255.254.0"
            match = re.search(r"inet addr:(\S+)", output)
            if match:
                return match.group(1)  # The captured group is the IP address
            else:
                return None
        except subprocess.CalledProcessError:
            # ifconfig command failed (interface may not exist)
            return None


