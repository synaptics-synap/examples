import json
import sys
import time
import threading
from utils.websockets import WebSockets
from synapRT.pipelines import pipeline


def main():
    ws_server = WebSockets(port=6789, index="./vision/index.html")
    ws_server.start()

    def handle_results(results, inference_time):
        message = json.dumps(results)
        ws_server.broadcast(message)

    pipe = pipeline(
        task="object-detection",
        model="/usr/share/synap/models/object_detection/body_pose/model/yolov8s-pose/model.synap",
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
