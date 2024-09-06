from typing import Optional

from gst.pipeline import GstPipeline
from utils.common import InputType, CAM_DEFAULT_WIDTH, CAM_DEFAULT_HEIGHT


class GstInputValidator:
    """Validates input sources by directing output to a fakesink"""

    def __init__(self, inp_type: int, num_buffers: int = 10, verbose: int = 1) -> None:
        self._inp_type = inp_type
        self._num_buffers = num_buffers
        self._verbose = verbose
        self._val_pipeline = GstPipeline()

    def validate_input(
        self,
        inp_src: str,
        msg_on_error: str,
        *,
        inp_w: Optional[int] = None,
        inp_h: Optional[int] = None,
        inp_codec: Optional[str] = None,
        codec_elems: Optional[tuple[str, str]] = None,
    ) -> bool:
        """
        Validates an input source.

        Args:
            inp_src (str): the input source (video file / camera device / RTSP stream URL)
            msg_on_error (str): message to display if the validation fails
            inp_w (int): [Optional] width of input source for camera
            inp_h (int): [Optional] height of input source for camera
            inp_codec (str): [Optional] codec used in compression (for video and RTSP)
            codec_elems (str): [Optional] Gstreamer elements for codec (for video and RTSP)
        """
        self._val_pipeline.reset()
        if self._inp_type == InputType.FILE:
            self._val_pipeline.add_elements(
                ["filesrc", f'location="{inp_src}"'],
                ["qtdemux", "name=demux", "demux.video_0"],
                "queue",
                *codec_elems,
            )
        elif self._inp_type == InputType.CAMERA:
            self._val_pipeline.add_elements(
                ["v4l2src", f"device={inp_src}"],
                f"video/x-raw,framerate=30/1,format=YUY2,width={inp_w or CAM_DEFAULT_WIDTH},height={inp_h or CAM_DEFAULT_HEIGHT}",
            )
        elif self._inp_type == InputType.RTSP:
            self._val_pipeline.add_elements(
                ["rtspsrc", f'location="{inp_src}"', "latency=2000"],
                "rtpjitterbuffer",
                ["rtph264depay", "wait-for-keyframe=true"],
                f"video/x-{inp_codec},width={inp_w},height={inp_h}" if (inp_w and inp_h) else f"video/x-{inp_codec}",
                *codec_elems,
            )
        self._val_pipeline.add_elements(
            ["fakesink", f"num-buffers={self._num_buffers}"]
        )
        if not self._val_pipeline.run(
            "Validating input..." if self._verbose > 0 else "", self._verbose > 1
        ):
            if self._verbose > 0:
                print("\n" + msg_on_error + "\n")
            return False
        if self._verbose > 0:
            print("Input OK")
        return True
