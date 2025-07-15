from synapRT.pipelines import pipeline
import json
import sys
import subprocess


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
        print("Unknown Processor")
        return "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"


def main():
    def handle_results(results, inference_time):
        message = json.dumps(results, indent=4)
        print(message)
        print(f"Inference Time: {inference_time:.0f} ms")

    # Accept model path as second argument, else use default
    model_path = sys.argv[2] if len(sys.argv) > 2 else get_model_path()
    pipe = pipeline(
        task="object-detection",
        model=model_path,
        profile=True,
        handler=handle_results,
    )

    print("Starting Object Detection Stream.")
    pipe(sys.argv[1])


if __name__ == "__main__":
    main()
