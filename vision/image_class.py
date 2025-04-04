import json
import sys
from synapRT.pipelines import pipeline


def load_labels(labels_file) -> list[str]:
    with open(labels_file, "r") as f:
        return json.load(f)["labels"]


def handle_results(results, inference_time):
    results = results["top_n"]
    print(f"Top {len(results)} results:\n")
    print(f"Class\tScore\tLabel")
    print(f"-----------------------------")
    for result in results:
        print(
            f"{result['class_index']:<6}  {result['confidence']:.2f}\t{labels[result['class_index']]:<20}"
        )
    if inference_time:
        print(f"\nInference time: {inference_time:.2f}ms")


if __name__ == "__main__":
    model = "/usr/share/synap/models/image_classification/imagenet/model/mobilenet_v2_1.0_224_quant/model.synap"
    image = "/usr/share/synap/models/image_classification/imagenet/sample/space_shuttle_224x224.jpg"
    labels = load_labels(
        "/usr/share/synap/models/image_classification/imagenet/info.json"
    )

    pipe = pipeline(
        task="image-classification",
        model=model,
        profile=True,
        handler=handle_results,
        top_n=5,
    )
    pipe(sys.argv[1])
