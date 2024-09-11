from argparse import ArgumentTypeError
from typing import Optional
import subprocess

from gst.validator import GstInputValidator
from utils.camera import find_valid_camera_devices
from utils.common import InputType, CAM_DEV_PREFIX, CAM_DEFAULT_WIDTH, CAM_DEFAULT_HEIGHT, CODECS


__all__ = [
    "get_dims",
    "get_bool_prop",
    "get_float_prop",
    "get_int_prop",
    "get_inp_type",
    "get_inp_src_info",
    "get_inf_model",
    "validate_inp_dims",
]


def get_dims(prompt: str, inp_dims: Optional[str]) -> tuple[int, int]:
    """
    Gets width and height from a widthxheight formatted string.

    Prompts user for dimensions string input if `inp_dims` is None.
    """
    while True:
        try:
            if not inp_dims:
                inp_dims = input(f"{prompt} (widthxheight): ")
            inp_w, inp_h = [int(d) for d in inp_dims.split("x")]
            if inp_w > 0 and inp_h > 0:
                return inp_w, inp_h
            print("\nDimensions must be positive integers\n")
            inp_dims = None
        except (ValueError, TypeError):
            print(f'\nInvalid dimensions "{inp_dims}"\n')
            inp_dims = None


def get_bool_prop(prompt: str) -> bool:
    """
    Gets a boolean (Y/n) property from user input.
    """
    while True:
        try:
            val = input(f"{prompt} (Y/n): ").lower()
            if val not in ("y", "n"):
                raise ValueError
            return val == "y"
        except (TypeError, ValueError):
            print(f"\nInvalid input\n")


def get_float_prop(prompt: str, prop_val: Optional[float], default: float, prop_min: float, prop_max: float) -> float:
    """
    Gets a float property in the range of `prop_range`.

    Prompts user for float input if `prop_val` is None.
    """
    while True:
        try:
            if prop_val is None:
                prop_val = float(input(f"{prompt} (default: {default}): ") or default)
            if prop_min <= prop_val <= prop_max:
                return prop_val
            print(f"\nValue must be >= {prop_min} and <= {prop_max}\n")
            prop_val = None
        except (TypeError, ValueError):
            print(f"\nInvalid input\n")
            prop_val = None


def get_int_prop(prompt: str, prop_val: Optional[int], default: int) -> int:
    """
    Gets a positive integer property.

    Prompts user for integer input if `prop_val` is None.
    """
    while True:
        try:
            if prop_val is None:
                prop_val = int(input(f"{prompt} (default: {default}): ") or default)
            if prop_val >= 0:
                return prop_val
            print("\nValue must be >= 0\n")
            prop_val = None
        except (TypeError, ValueError):
            print(f"\nInvalid input\n")
            prop_val = None


def get_inp_type(inp_src: str) -> InputType:
    if inp_src.startswith(CAM_DEV_PREFIX) or inp_src.lower() == "auto":
        return InputType.CAMERA
    elif inp_src.startswith("rtsp://"):
        return InputType.RTSP
    open(inp_src, "rb").close()
    return InputType.FILE


def get_inp_src_info(
    inp_w: Optional[int],
    inp_h: Optional[int],
    inp_src: Optional[str],
    inp_codec: Optional[str],
    inp_type: Optional[InputType] = None,
) -> Optional[tuple[int, str, str, tuple[str, str]]]:
    """
    Gets codec details from a provided input source.

    Prompts user for missing information and also validates the input source.
    """
    inp_src: str = inp_src or input("Input source: ")
    if not inp_type:
        try:
            inp_type: InputType = get_inp_type(inp_src)
        except FileNotFoundError:
            print(f"\nERROR: Invalid input source \"{inp_src}\"\n")
            return None
    gst_val: GstInputValidator = GstInputValidator(inp_type)
    codec_elems: Optional[tuple[str, str]] = None
    try:
        if inp_type == InputType.CAMERA:
            inp_codec = None
            if inp_src.lower() == "auto":
                print("Finding valid camera device...")
                valid_devs = find_valid_camera_devices(inp_w or CAM_DEFAULT_WIDTH, inp_h or CAM_DEFAULT_HEIGHT)
                if not valid_devs:
                    print("\nNo camera connected to board\n")
                    return None
                inp_src = valid_devs[0]
                print(f"Found {inp_src}")
                return inp_type, inp_src, inp_codec, codec_elems
            msg_on_error: str = (
                f'ERROR: Invalid camera "{inp_src}", use `v4l2-ctl --list-devices` to verify device'
            )
        elif inp_type == InputType.FILE or inp_type == InputType.RTSP:
            inp_codec = inp_codec or (
                input("[Optional] Codec [av1 / h264 (default) / h265]: ") or "h264"
            )
            codec_elems = CODECS[inp_codec]
            msg_on_error: str = (
                f'ERROR: Invalid input video file "{inp_src}", check source and codec'
            ) if inp_type == InputType.FILE else (
                f'ERROR: Invalid RTSP stream "{inp_src}", check URL and codec'
            )
        else:
            raise SystemExit("Fatal: invalid input parameters")

        if gst_val.validate_input(
            inp_src,
            msg_on_error,
            inp_w=inp_w,
            inp_h=inp_h,
            inp_codec=inp_codec,
            codec_elems=codec_elems,
        ):
            return inp_type, inp_src, inp_codec, codec_elems
    except KeyError:
        print(
            f'\nERROR: Invalid codec "{inp_codec}", choose from [av1 / h264 / h265]\n'
        )


def get_inf_model(model: Optional[str]) -> str:
    """
    Gets a valid model by verifying model with synap_cli.

    Prompts user for model file if `model` is None.
    """
    while True:
        try:
            if not model:
                model: str = input("Model file path: ")
            print("Validating model...")
            # fmt: off
            subprocess.run(
                [
                    "synap_cli",
                    "-m", model,
                    "random"
                ],
                check=True,
                capture_output=True
            )
            # fmt: on
            print("Model OK")
            return model
        except subprocess.CalledProcessError as e:
            print("\n" + e.stderr.decode())
            print(f'\nERROR: Invalid SyNAP model "{model}"\n')
            model = None


def validate_inp_dims(dims: Optional[str]) -> str:
    """
    Helper function to validate input dimensions from a command line arg.
    """
    try:
        if dims is None:
            return ""
        width, height = dims.split("x")
        width: int = int(width)
        height: int = int(height)
        if width <= 0 or height <= 0:
            raise ArgumentTypeError("Both width and height must be positive integers.")
        return f"{width}x{height}"
    except ValueError:
        raise ArgumentTypeError(
            "Input size must be WIDTHxHEIGHT, where both are integers."
        )
