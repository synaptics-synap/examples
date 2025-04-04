import subprocess
import warnings

try:
    import gi

    gi.require_version("GUdev", "1.0")
    from gi.repository import GUdev

    GLIB_AVAILABLE = True
except ImportError:
    GLIB_AVAILABLE = False
    warnings.warn("Unable to import gi, camera detection defaulting to /dev/video7")

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    warnings.warn("Unable to import cv2, photo capture may not work properly")


def get_camera_devices(cam_subsys: str = "video4linux") -> list[str]:
    if not GLIB_AVAILABLE:
        return ["/dev/video7"]

    camera_paths: list[str] = []
    client = GUdev.Client(subsystems=[cam_subsys])
    devices = client.query_by_subsystem(cam_subsys)

    for device in devices:
        bus = device.get_property("ID_BUS")
        if bus == "usb":
            sys_path = device.get_sysfs_path()
            if sys_path:
                index_path = f"{sys_path}/index"
                try:
                    with open(index_path, "r") as f:
                        contents = f.read().strip()
                        index_val = int(contents)

                        if index_val == 0:
                            dev_node = device.get_device_file()
                            if dev_node:
                                camera_paths.append(dev_node)
                except OSError as e:
                    warnings.warn(f"Warning: Error reading {index_path}: {e}")
                except ValueError:
                    warnings.warn(
                        f"Warning: Unexpected contents in {index_path}: {contents}"
                    )

    return camera_paths


def capture(device=None, filename="out.jpg"):
    try:
        device = device or get_camera_devices()[0]
    except IndexError:
        warnings.warn("Valid camera device not found, defaulting to /dev/video7")
        device = "/dev/video7"
    # Set the video format to MJPG at 640x480.
    fmt_cmd = [
        "v4l2-ctl",
        f"--device={device}",
        "--set-fmt-video=width=640,height=480,pixelformat=MJPG",
    ]
    try:
        subprocess.run(fmt_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error setting format:")
        print(e.stderr)
        return False

    # Capture one frame to a file.
    capture_cmd = [
        "v4l2-ctl",
        f"--device={device}",
        "--stream-mmap",
        "--stream-count=1",
        f"--stream-to={filename}",
    ]
    try:
        subprocess.run(capture_cmd, capture_output=True, text=True, check=True)
        # print(f"Image saved as {filename}")
        if CV2_AVAILABLE:
            cv2.imwrite(filename, cv2.imread(filename))
        return True
    except subprocess.CalledProcessError as e:
        print("Error capturing image:")
        print(e.stderr)
        return False


if __name__ == "__main__":
    capture()
