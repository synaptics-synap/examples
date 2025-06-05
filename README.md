# Synaptics Astra SL16xx Series AI Examples

![home](/samples/home.png)

This repository provides AI example applications for the **Synaptics Astra SL16xx** series, covering **computer vision, speech processing, and large language models (LLMs)**. Follow the instructions below to set up your environment and run various AI examples in few minutes.

The examples in this repository are designed to work with Astra SL1680 processor using Astra Machina Dev Kit. Vision examples leverage NPU and other examples leverage CPU.

> **Note:** For Astra SL1640 processor (leveraging NPU), these examples can be still run, after adding required set of packages into the OOBE image via bitbake.
> 
> **Note:** For Astra SL1640 processor (leveraging GPU), Vision examples need to be modified for GPU (instead of NPU), after adding required set of packages into the OOBE image via bitbake.


## Learn more about Synaptics Astra by visiting:

- [Astra](https://www.synaptics.com/products/embedded-processors) – Explore the Astra AI platform.
- [Astra Machina](https://www.synaptics.com/products/embedded-processors/astra-machina-foundation-series) – Discover our powerful development kit.
- [AI Developer Zone](https://developer.synaptics.com/) – Find step-by-step tutorials and resources.


## Setting up Astra Machina Board
For instructions on how to set up Astra Machina board , see the  [Setting up the hardware](https://synaptics-astra.github.io/doc/v/1.5.0/quickstart/hw_setup.html)  guide.


## 🔧 Installation
 

### Clone the Repository

Clone the repository using the following command:

```bash
git clone https://github.com/synaptics-synap/examples.git
```
Navigate to the Repository Directory:

```bash
cd examples
```

### Setup Python Environment

To get started, set up your Python environment. This step ensures all required dependencies are installed and isolated within a virtual environment:

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Install SynapRT 
[SynapRT](https://github.com/synaptics-synap/synap-rt) Python package allows you to run real-time AI pipelines on your Synaptics Astra board in just a few lines of code:

```bash
pip install https://github.com/synaptics-synap/synap-rt/releases/download/v0.0.1-preview/synap_rt-0.0.1-py3-none-any.whl
```

## 🎯 Running AI Examples

### 🖼️ Vision
To run a YOLOv8-small  image classification model on a Image:
```bash
 python3 -m vision.image_class out.jpg
```

To run a YOLOv8-small body pose model using a connected camera and you can Infer results using :
```bash
python3 -m vision.body_pose 'cam'
```
![bodypose](/samples/body-pose.gif)


 

### 🗣️ Speech-to-Text

**Moonshine** is an speech-to-text model that provides translation from speech to text.

To transcribe an audio file ( for example`jfk.wav`):
```bash
python3 -m speech_to_text.moonshine 'samples/jfk.wav'
```

To enable real-time speech transcription using a **USB microphone** (such as one from a Webcam or a Headphone):
```bash
python3 -m speech_to_text.pipeline
```

 

### 🔊 Text-to-Speech
Convert a given text string into synthetic speech using **Piper**:
```bash
python3 -m text_to_speech.piper "synaptics astra example"
```

### 🚀 Large Language Models (LLMs)


##### Install SQLite3 Dependencies
SQLite3 is required for certain AI model operations. Install it using the following commands:
```bash
wget https://synaptics-astra-labs.s3.us-east-1.amazonaws.com/downloads/sqlite3_3.38.5-r0_arm64.deb
wget https://synaptics-astra-labs.s3.us-east-1.amazonaws.com/downloads/python3-sqlite3_3.10.13-r0_arm64.deb
dpkg -i python3-sqlite3_3.10.13-r0_arm64.deb sqlite3_3.38.5-r0_arm64.deb
```

#### 🦙 Install `llama-cpp-python`

This command installs **llama-cpp-python**, which enables running large language models efficiently:
```bash
pip install llama-cpp-python
```

There is also a prebuilt version, this installs faster but lags version and may not support newer models (e.g. deepseek)
```
pip install llama-cpp-python   --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

To run large language models such as **Qwen** and **DeepSeek**:

```bash
python3 -m llm.qwen
#python3 -m llm.deepseek
```
![qwen](/samples/qwen.gif)

### 🔍 Embeddings
Get a gist for Embeddings and how to generate sentence embeddings using **MiniLM**, a lightweight transformer-based model:
```bash
python3 -m embeddings.minilm "synaptics astra example!"
```

 
### 🤖 AI - Text Assistant
Launch an AI-powered text assistant with Tool calling functionality:
```bash
python3 -m assistant.toolcall
```

 
## Running gstreamer example
Use SyNAP GStreamer Plugins to run Real-time inference on a video input using Python

```bash
python3 -m examples.infer_video -i /home/root/video.mp4 --fullscreen
```

![od](/samples/od.gif)


## 📚 Additional Resources

- [AI Developer Zone](https://developer.synaptics.com/) – Find step-by-step tutorials and resources.
- [GitHub Synap-RT](https://github.com/synaptics-synap/synap-rt) – ExploreReal-time AI pipelines with Python.
- [GitHub SyNAP-Python-API](https://github.com/synaptics-synap/synap-python) – Python bindings that closely mirror our SyNAP C++ API.
- [GitHub SyNAP C++](https://github.com/synaptics-astra/synap-framework) – Low-level access to our SyNAP C++ AI Framework
- [GitHub Astra SDK](https://github.com/synaptics-astra) – Get started with the Astra SDK for AI development.

## Contributing

We encourage and appreciate community contributions! Here’s how you can get involved:

- **Contribute to our [Community](./community)** – Share your work and collaborate with other developers.
- **Suggest Features and Improvements** – Have an idea? Let us know how we can enhance the project.
- **Report Issues and Bugs** – Help us improve by identifying and reporting any issues.

Your contributions make a difference, and we look forward to your input!

## License

This project is licensed under the **Apache License, Version 2.0**.  
See the [LICENSE](./LICENSE) file for details.
