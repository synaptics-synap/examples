# Real-time Video Inference with Python
This project uses Python3.10 to demo real-time inference on a video input on the Synaptics Astra SL1680 board.
> [!IMPORTANT]
> The firmware version on the SL1680 board must be >=1.0.0

## Running demos
The demos are in the form of self-contained, executable zip archives (`.pyz`) and are located in the [exec](exec) folder. There are specific demos for each supported input type (camera, file, RTSP) and a more generic demo that's compatible will all supported inputs. To run a demo, first download it to your board and then do:
```
python3 <demo>.pyz
```
### Run options
The demos can also be run with optional input arguments. Here's a few examples:

#### 1. Camera demo with pre-loaded pose model
```
python3 demo_camera.pyz \
-m /usr/share/synap/models/object_detection/body_pose/model/yolov8s-pose/model.synap
```

#### 2. Fullscreen video demo on a specific video file
```
python3 demo_video.pyz \
-i /home/root/video.mp4 \
--fullscreen
```

#### 3. Generic demo with an input source, model and inference parameters
```
python3 demo.pyz \
-i /home/root/video.mp4 \
-m /home/root/model.synap \
--input_codec h264 \
--confidence_threshold 0.85 \
--inference_skip 0
```

The full list of available input options for each demo can be viewed with `python3 <demo>.pyz --help`.

## Customizing and Extending demos
The functionality of the demos and their components can be extended, for example, to create a demo for a custom use-case.

To begin, clone the examples repository to your development machine or SL1680 board and navigate to the `video_inference` folder.

The source code for the input specific demos is in [examples](examples). These have some pre-defined parameters that can be modified in the source code. Additionally the [`gst`](gst) and [`utils`](utils) modules contain classes and functions that can be used to build custom demos.

To build demos into a self-contained executable zip archive (`.pyz`), place the demo source code in [examples](examples). Then run:
```
python3 pyz_builder.py --target your_demo.py
```
This will generate `your_demo.pyz` in the [exec](exec) folder which can be run just like any of the other demos.

> [!TIP]
> You can also directly run `python3 -m examples.your_demo` to test without building