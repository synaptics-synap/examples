# Real-time Video Inference with Python
This project uses Python3.10 to demo real-time inference on a video input on the Synaptics Astra SL1680 board.
> [!IMPORTANT]
> The firmware version on the SL1680 board must be >=1.0.0

## Running examples
Clone the examples repository and navigate to the `video_inference` folder.
All examples are located in the [`examples`](examples) folder. There are specific examples for each supported input type (camera, file, RTSP) and a more generic example that's compatible with all supported inputs. To run an example:
```sh
python3 -m examples.<example>
```
### Run options
The examples can also be run with optional input arguments. Here's a few examples:

#### 1. Camera demo with pre-loaded pose model
```sh
python3 -m examples.infer_camera \
-m /usr/share/synap/models/object_detection/body_pose/model/yolov8s-pose/model.synap
```

#### 2. Fullscreen video demo on a specific video file
```sh
python3 -m examples.infer_video \
-i /home/root/video.mp4 \
--fullscreen
```

#### 3. Generic demo with an input source, model and inference parameters
```sh
python3 -m examples.infer \
-i /home/root/video.mp4 \
-m /home/root/model.synap \
--input_codec h264 \
--confidence_threshold 0.85 \
--inference_skip 0
```

The full list of available input options for each demo can be viewed with `python3 -m examples.<example>.py --help`.

### Building demos from examples
The `pyz_builder.py` script can package examples into self-contained, executable `.pyz` zip archives. It has the following options:
1. `--all | --targets example [example ...]`
    Build all examples in the [`examples`](examples) folder or specific example(s).
2. `-o/--output_dir`
    The directory to store built .pyz files in. The default is "./build".

Demos have the same run options as the examples and can be run with `python3 <demo>.pyz`.

## Customizing and Extending Examples
The functionality of the examples and their components can be extended, for example, to create an example for a custom use-case.

To begin, clone the examples repository to your development machine or SL1680 board and navigate to the `video_inference` folder.

The input specific examples have some pre-defined parameters that can be modified in the source code. Additionally the [`gst`](gst) and [`utils`](utils) modules contain classes and functions that can be used to build custom demos.

### SyNAP GStreamer Plugins
The [`gst`](gst) module creates a GStreamer pipeline that uses the SyNAP GStreamer plugins for streaming and real-time video inference. Many of the input arguments such as `-m/--model` are directly passed to these plugins by `gst`. Documentation on the GStreamer plugins can be found here: https://synaptics-astra.github.io/doc/v/1.1.0/linux/index.html#gstreamer-synap-plugin

### Building a Custom Demo
Place the demo source code in the [examples](examples) folder. Then follow the instructions for [building demos from examples](#building-demos-from-examples).