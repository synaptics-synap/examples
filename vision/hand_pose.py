import argparse
import os
import sys
import logging

from hand_detection import SynapHandDetectionPipeline

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run palm and hand landmark detection using SyNAP on live camera or image input"
    )
    parser.add_argument(
        "-m", "--model-dir", required=True,
        help="Path to directory containing 'palm_model.synap' and 'hand_model.synap'"
    )
    parser.add_argument(
        "-i", "--input", default="camera",
        help="Input source: 'camera' or image file path"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()

def validate_models(model_dir):
    palm_path = os.path.join(model_dir, "palm_model.synap")
    hand_path = os.path.join(model_dir, "hand_model.synap")
    if not os.path.isfile(palm_path) or not os.path.isfile(hand_path):
        sys.exit("Error: palm_model.synap and/or hand_model.synap not found in model directory")
    return {"palm": palm_path, "hand": hand_path}

def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    model_paths = validate_models(args.model_dir)

    pipeline = SynapHandDetectionPipeline(model=model_paths)
    try:
        pipeline(args.input)
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Exiting...")
    except Exception as e:
        logging.exception(f"Runtime error: {e}")

if __name__ == "__main__":
    main()
