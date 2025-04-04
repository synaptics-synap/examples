from synapRT.pipelines import pipeline
import json
import sys


def main():
    def handle_results(results, inference_time):
        message = json.dumps(results, indent=4)
        print(message)
        print(f"Inference Time: {inference_time:.0f} ms")

    pipe = pipeline(
        task="object-detection",
        model="/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap",
        profile=True,
        handler=handle_results,
    )

    print("Starting Object Detection Stream.")
    pipe(sys.argv[1])


if __name__ == "__main__":
    main()
