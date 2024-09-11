# ============================================================================== #
# IMPORTS: DO NOT MODIFY                                                         #
# ============================================================================== #

import argparse
import sys
from typing import Any

from gst.pipeline import GstPipelineGenerator
from utils.model_info import get_model_input_dims
from utils.user_input import get_inp_src_info, get_inf_model, validate_inp_dims
from utils.common import InputType

# ============================================================================== #


# RTSP stream URL.
# Leaving this empty will prompt the script to ask for a URL when run.
RTSP_URL = ""

# The codec used to compress the RTSP stream.
# Must be one of: av1, h264, h265
# Try using a different codec if the demo fails to run
VIDEO_CODEC = "h264"

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
        inp_w, inp_h = [int(d) for d in args.input_dims.split("x")] if args.input_dims else (None, None)
        inp_src_info = get_inp_src_info(inp_w, inp_h, args.input, args.input_codec, inp_type=InputType.RTSP)
        if not inp_src_info:
            sys.exit(1)
        model = get_inf_model(args.model)
        model_inp_dims = get_model_input_dims(model)
        if not model_inp_dims:
            sys.exit(1)
        gst_params: dict[str, Any] = {
            "inp_type": InputType.RTSP,
            "inp_w": inp_w,
            "inp_h": inp_h,
            "inp_src": inp_src_info[1],
            "inp_codec": inp_src_info[2],
            "codec_elems": inp_src_info[3],
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
        default=RTSP_URL,
        metavar="URL",
        help="RTSP stream URL (default: %(default)s)"
    )
    parser.add_argument(
        "-d", "--input_dims",
        type=validate_inp_dims,
        default=None,
        metavar="WIDTHxHEIGHT",
        help="[Optional] RTSP stream's input size (widthxheight)"
    )
    parser.add_argument(
        "-c", "--input_codec",
        type=str,
        default=VIDEO_CODEC,
        metavar="CODEC",
        help="RTSP stream input codec (default: %(default)s)",
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
        help="How many frames to skip between sucessive inferences (default: %(default)s)"
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
