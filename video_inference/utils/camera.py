from gst.validator import GstInputValidator
from utils.common import InputType, CAM_DEV_PREFIX, CAM_DEFAULT_WIDTH, CAM_DEFAULT_HEIGHT


def find_valid_camera_devices(
    inp_w: int = CAM_DEFAULT_WIDTH,
    inp_h: int = CAM_DEFAULT_HEIGHT,
) -> list[str]:
    """
    Attempts to find a connected camera.

    Only works for devices with format "dev/videoX".
    """
    if not inp_w > 0 or not inp_h > 0:
        raise ValueError("Invalid camera input dimensions")
    val = GstInputValidator(inp_type=InputType.CAMERA, verbose=0)
    valid_devs: list[str] = []
    for i in range(10):
        if val.validate_input(CAM_DEV_PREFIX + str(i), "", inp_w=inp_w, inp_h=inp_h):
            valid_devs.append(CAM_DEV_PREFIX + str(i))
    return valid_devs
