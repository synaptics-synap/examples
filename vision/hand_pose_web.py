import json
import sys
import time
import threading
import signal

from utils.websockets import WebSockets
from synapRT.pipelines import pipeline


def main():
    # Start the WebSocket server (port 6790 will fallback automatically if in use)
    ws_server = WebSockets(port=6790, index="./vision/index.html")
    ws_server.start()
    print(f"[INFO] WebSocket server running on ws://{ws_server.host}:{ws_server.port}")

    # Handle Ctrl+C and SIGTERM gracefully
    def shutdown_handler(sig, frame):
        print("[INFO] Shutting down gracefully...")
        ws_server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Broadcast inference results to all WebSocket clients
    def handle_results(results, inference_time):
        print(f"[DEBUG] Sending results: {results}")
        message = json.dumps(results)
        ws_server.broadcast(message)


    # Build the pipeline
    pipe = pipeline(
        task="hand-detection",
        model={
            "palm": "./vision/palm.synap",
            "hand": "./vision/hand.synap",
        },
        handler=handle_results,
        profile=True,
    )

    print("[INFO] Starting Hand Pose Stream...")
    pipe_thread = threading.Thread(target=pipe, args=(sys.argv[1],), daemon=True)
    pipe_thread.start()

    try:
        while True:
            _, res = pipe.poll()
            if pipe.error:
                raise pipe.error
            if pipe.finished:
                break
            time.sleep(0.001)
    except KeyboardInterrupt:
        shutdown_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"[ERROR] {e}")
        shutdown_handler(signal.SIGTERM, None)


if __name__ == "__main__":
    main()
