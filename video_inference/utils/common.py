from enum import Enum, auto
from typing import Final

# synap metadata file
INF_META_FILE: Final = "0/model.json"

# camera specific constants
CAM_DEV_PREFIX = "/dev/video"
CAM_DEFAULT_WIDTH = 640
CAM_DEFAULT_HEIGHT = 480

# video codecs
CODECS: dict[str, tuple[str, str]] = {
    "av1": ("av1parse", "v4l2av1dec"),
    "h264": ("h264parse", "avdec_h264"),
    "h265": ("h265parse", "avdec_h265"),
}


class InputType(Enum):
    CAMERA = auto()
    FILE = auto()
    RTSP = auto()
