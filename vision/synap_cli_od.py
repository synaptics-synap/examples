import argparse
import os

from synap import Network
from synap.preprocessor import Preprocessor
from synap.postprocessor import Detector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="synap model")
    parser.add_argument("input", help="input image")
    args = parser.parse_args()

    args.model = args.model or "model.synap"
    if not os.path.exists(args.model):
        raise FileNotFoundError("'model.synap' not found")

    network = Network(args.model)
    preprocessor = Preprocessor()
    detector = Detector()
    print()
    print(args.input)

    assigned_rect = preprocessor.assign(network.inputs, args.input)
    outputs = network.predict()
    result = detector.process(outputs, assigned_rect)

    print("#   Score  Class   Position        Size  Description     Landmarks")
    for i, item in enumerate(result.items):
        bb = item.bounding_box
        print(
            f"{i:<3}  {item.confidence:.2f} {item.class_index:>6}  {bb.origin.x:>4},{bb.origin.y:>4}   {bb.size.x:>4},{bb.size.y:>4}  {'':<16}",
            end="",
        )
        for lm in item.landmarks:
            print(f" {lm}", end="")
        print()


if __name__ == "__main__":
    main()
