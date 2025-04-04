"""
Python script to receive JSON data over UDP
"""

import argparse
import json
import os
import socket
import subprocess
import time


def main():
    udp_ip = args.ip_address
    udp_port = args.port
    timeout_s = args.timeout
    buffer_sz = args.buffer_size

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    sock.setblocking(False)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_sz)

    print(f"Listening for JSON data on {udp_ip}:{udp_port}")
    data: bytes = None
    last_data_ts: float = time.time()
    while True:
        try:
            while True:
                try:
                    data, _ = sock.recvfrom(buffer_sz)
                    last_data_ts = time.time()
                except BlockingIOError:
                    break

            if time.time() - last_data_ts > timeout_s:
                print(f"No data received for {timeout_s} seconds, exiting...")
                break

            if data:
                try:
                    json_data = json.loads(data.decode("utf-8"))
                    json_output = json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    json_output = "Failed to decode JSON data"
                finally:
                    data = None

                subprocess.run(["cls" if os.name == "nt" else "clear"], shell=True)
                print(json_output)

            # time.sleep(0.01)  # uncomment to lower cpu usage (warning: might cause desync)

        except KeyboardInterrupt:
            print(f"Ctrl+C detected, exiting...")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-a",
        "--ip_address",
        metavar="ADDR",
        type=str,
        default="0.0.0.0",
        help="IP address to bind to (default: %(default)s (bind to all available interfaces))",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5000,
        help="Port to listen on (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        metavar="SECONDS",
        type=int,
        default=5,
        help="Timeout for exiting when no data is received (default: %(default)s)",
    )
    parser.add_argument(
        "-b",
        "--buffer_size",
        metavar="SIZE",
        type=int,
        default=1024,
        help="UDP receiver data buffer size (in bytes) (default: %(default)s)",
    )
    args = parser.parse_args()
    main()
