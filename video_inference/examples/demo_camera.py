# ============================================================================== #
# IMPORTS: DO NOT MODIFY                                                         #
# ============================================================================== #

import argparse
import sys
from typing import Any

from gst.pipeline import GstPipelineGenerator
from utils.model_info import get_model_input_dims
from utils.user_input import get_inp_src_info, get_inf_model, validate_inp_dims
from utils.common import InputType, CAM_DEFAULT_WIDTH, CAM_DEFAULT_HEIGHT

# ============================================================================== #


# Your camera's device ID, typically has the format "/dev/videoX". "AUTO" means the script will attempt to find your camera.
# Note that "AUTO" might find the wrong camera if you have multiple cameras connected to the baord.
# Execute `v4l2-ctl --list-devices` to get a list of connected camera devices and their device IDs.
CAMERA = "AUTO"

# Your camera's input width.
INPUT_WIDTH = CAM_DEFAULT_WIDTH   # 640

# Your camera's input height.
INPUT_HEIGHT = CAM_DEFAULT_HEIGHT # 480

# The path to the inference model to use. Must be a vaild SyNAP model with a ".synap" file extension.
MODEL = "/usr/share/synap/models/object_detection/coco/model/yolov8s-640x384/model.synap"

# How many frames to skip between sucessive inferences.
# Increasing this number may result in better performance but can look worse visually.
INFERENCE_SKIP = 1

# Maximum number of inference results to display per frame
MAX_RESULTS = 5

# Confidence threshold, only detections with scores above this will be considered valid
CONF_THRESHOLD = 0.5

# Whether to launch the demo in fullscreen.
FULLSCREEN = False


# ============================================================================== #
# RUNNER CODE: DO NOT MODIFY                                                     #
# ============================================================================== #

def main():
    try:
        inp_w, inp_h = [int(d) for d in args.input_dims.split("x")]
        inp_src_info = get_inp_src_info(inp_w, inp_h, args.input, None)
        if not inp_src_info:
            sys.exit(1)
        model = get_inf_model(args.model)
        model_inp_dims = get_model_input_dims(model)
        if not model_inp_dims:
            sys.exit(1)
        gst_params: dict[str, Any] = {
            "inp_type": InputType.CAMERA,
            "inp_w": inp_w,
            "inp_h": inp_h,
            "inp_src": inp_src_info[1],
            "inf_model": model,
            "inf_w": model_inp_dims[0],
            "inf_h": model_inp_dims[1],
            "inf_skip": args.inference_skip,
            "inf_max": args.num_inferences,
            "inf_thresh": args.confidence_threshold,
            "fullscreen": args.fullscreen,
        }
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()

    gen: GstPipelineGenerator = GstPipelineGenerator(gst_params)

    gen.make_pipeline()
    gen.pipeline.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=CAMERA,
        metavar="DEVICE",
        help="Connected camera device ID (default: %(default)s)"
    )
    parser.add_argument(
        "-d", "--input_dims",
        type=validate_inp_dims,
        default=f"{INPUT_WIDTH}x{INPUT_HEIGHT}",
        metavar="WIDTHxHEIGHT",
        help="Camera's input size (widthxheight) (default: %(default)s)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default=MODEL,
        metavar="FILE",
        help="SyNAP model file location (default: %(default)s)"
    )
    parser.add_argument(
        "-s", "--inference_skip",
        type=int,
        default=INFERENCE_SKIP,
        metavar="FRAMES",
        help="How many frames to skip between each inference (default: %(default)s)"
    )
    parser.add_argument(
        "-n",
        "--num_inferences",
        type=int,
        metavar="N_RESULTS",
        default=MAX_RESULTS,
        help="Maximum number of detections returned per frame (default: %(default)s)"
    )
    parser.add_argument(
        "-t",
        "--confidence_threshold",
        type=float,
        metavar="SCORE",
        default=CONF_THRESHOLD,
        help="Confidence threshold for inferences (default: %(default)s)"
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        default=FULLSCREEN,
        help="Launch demo in fullscreen",
    )
    args = parser.parse_args()
    main()

# ============================================================================== #
