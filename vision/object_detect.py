
from synapRT.pipelines import pipeline
from utils.websockets import WebSockets
import json
import sys

def main():
    ws_server = WebSockets(port=6789)
    ws_server.start()

    def handle_results(results, inference_time):
        message = json.dumps(results)
        ws_server.broadcast(message)

    pipe = pipeline(
        task="object-detection",
        model="/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap",
        profile=True,
        handler=handle_results,
    )

    print("Starting Object Dectection Stream.")
    pipe(sys.argv[1])

if __name__ == "__main__":
    main()
