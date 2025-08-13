import json
import sys
import time
import threading
import subprocess
from utils.websockets import WebSockets
from synapRT.pipelines import pipeline


def get_model_path():
    try:
        hostname = subprocess.check_output(['cat', '/etc/hostname']).decode().strip()
    except Exception:
        hostname = ""
    if hostname == "sl1620":
        return "/usr/share/synap/models/object_detection/coco/model.synap"
    elif hostname in ("sl1680", "sl1640"):
        return "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"
    else:
        print("Unknown processor")
        return "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"

def main():
    ws_server = WebSockets(port=6789, index="./vision/index.html")
    ws_server.start()

    def handle_results(results, inference_time):
        message = json.dumps(results)
        ws_server.broadcast(message)

    # Accept model path as second argument, else use default
    model_path = sys.argv[2] if len(sys.argv) > 2 else get_model_path()
    pipe = pipeline(
        task="object-detection",
        model=model_path,
        profile=True,
    )

    print("Starting Body Pose Stream.")
    pipe_thread = threading.Thread(target=pipe, args=(sys.argv[1],))
    pipe_thread.start()

    try:
        while True:
            _, res = pipe.poll()
            if res:
                handle_results(res, pipe.inference_time)
            if pipe.error:
                raise pipe.error
            if pipe.finished:
                break
            time.sleep(0.001)  # to stop busy waiting
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
