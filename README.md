# Synaptics Astra SL16xx Series AI Examples

![home](/samples/home.png)

This repository provides AI example applications for the **Synaptics Astra SL16xx** series, covering **computer vision, speech processing, and large language models (LLMs)**. Follow the instructions below to set up your environment and run various AI examples in few minutes.

The examples in this repository are designed to work with Astra SL1680 processor using Astra Machina Dev Kit. Vision examples leverage NPU and other examples leverage CPU.

> **Note:** For Astra SL1640 processor (leveraging NPU), these examples can be still run, after adding required set of packages into the OOBE image via bitbake.
> 
> **Note:** For Astra SL1620 processor (leveraging GPU), Vision - Classification Model is not pre-installed. Other examples can be still run, after adding required set of packages into the OOBE image via bitbake.


## Learn more about Synaptics Astra by visiting:

- [Astra](https://www.synaptics.com/products/embedded-processors) – Explore the Astra AI platform.
- [Astra Machina](https://www.synaptics.com/products/embedded-processors/astra-machina-foundation-series) – Discover our powerful development kit.
- [AI Developer Zone](https://developer.synaptics.com/) – Find step-by-step tutorials and resources.


## Setting up Astra Machina Board
For instructions on how to set up Astra Machina board , see the  [Setting up the hardware](https://synaptics-astra.github.io/doc/v/latest/quickstart/hw_setup.html)  guide.


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
```

For Astra OOBE SDK 2.0 (scarthgap) and above, Please use Python3.12 packages:
```
pip install -r requirements-py312.txt
```

For Astra OOBE SDK 1.8 (kirkstone) and below, Please use Python3.10 packages:

```
pip install -r requirements.txt
```



## 🎯 Running AI Examples

### 🖼️ Vision
To run a YOLOv8-small  image classification model on a Image:
```bash
python3 -m vision.image_class samples/fish.jpg
```



To run a YOLOv8-small body pose model using a connected camera and you can Infer results using :
```bash
python3 -m vision.body_pose 'cam'
```
![bodypose](/samples/body-pose.gif)


 

### 🗣️ Speech-to-Text

**Moonshine** is a speech-to-text model that provides translation from speech to text.

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

> **Note:** This example application uses the piper-tts Python package, which, starting with version 1.3.0, is available under a GPL3 license. Depending on your organization, this may be incompatible with production usage.

```bash
python3 -m text_to_speech.piper "synaptics astra example"
```

### 🚀 Large Language Models (LLMs)


##### Install SQLite3 Dependencies
> [!WARNING]
> This step will overwrite existing `sqlite3` libraries if present. It is recommended to verify that `sqlite3` isn't installed before continuing:
> ```
> (ls /usr/lib/libsqlite3* 1>/dev/null && python3 -c "import sqlite3") && echo "sqlite3 available"
> ```
SQLite3 is required for certain AI model operations and may not be pre-installed in SDK <1.6.0. Install it using the following commands:
```bash
wget https://synaptics-synap.github.io/examples-prebuilts/packages/sqlite3_3.38.5-r0_arm64.deb
wget https://synaptics-synap.github.io/examples-prebuilts/packages/python3-sqlite3_3.10.13-r0_arm64.deb
dpkg -i python3-sqlite3_3.10.13-r0_arm64.deb sqlite3_3.38.5-r0_arm64.deb
```

#### 🦙 Install `llama-cpp-python`

This command installs **llama-cpp-python**, which enables running large language models efficiently.
We have our prebuilt version for Astra.

For Astra OOBE SDK 2.0 (scarthgap) and above, Please use Python 3.12 version:
```
pip install https://synaptics-synap.github.io/examples-prebuilts/packages/llama_cpp_python-0.3.16-cp312-cp312-linux_aarch64.whl
```

For Astra OOBE SDK 1.8 (kirkstone) and below, Please use Python 3.10 version: 
```
pip install https://synaptics-synap.github.io/examples-prebuilts/packages/llama_cpp_python-0.3.14-cp310-cp310-linux_aarch64.whl
```

To run large language models such as  **Gemma**, **Qwen** and **DeepSeek**:

**For interactive chat example:** 
```bash
python3 -m llm.gemma
```

**For chat completion example:**
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
Please see [synap-rt](https://github.com/synaptics-synap/synap-rt) for running real-time GStreamer based inference


## 📚 Additional Resources

- [AI Developer Zone](https://developer.synaptics.com/) – Find step-by-step tutorials and resources.
- [GitHub Synap-RT](https://github.com/synaptics-synap/synap-rt) – ExploreReal-time AI pipelines with Python.
- [GitHub SyNAP-Python-API](https://github.com/synaptics-synap/synap-python) – Python bindings that closely mirror our SyNAP C++ API.
- [GitHub SyNAP C++](https://github.com/synaptics-astra/synap-framework) – Low-level access to our SyNAP C++ AI Framework
- [GitHub Astra SDK](https://github.com/synaptics-astra) – Get started with the Astra SDK for AI development.
- [GitHub Examples Pre-builts](https://github.com/synaptics-synap/examples-prebuilts) – Pre-built packages for Astra Machina.

  
## Contributing

We encourage and appreciate community contributions! Here’s how you can get involved:

- **Contribute to our [Community](./community)** – Share your work and collaborate with other developers.
- **Suggest Features and Improvements** – Have an idea? Let us know how we can enhance the project.
- **Report Issues and Bugs** – Help us improve by identifying and reporting any issues.

Your contributions make a difference, and we look forward to your input!

## License

This project is licensed under the **Apache License, Version 2.0**.  
See the [LICENSE](./LICENSE) file for details.
