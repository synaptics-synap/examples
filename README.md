# Synaptics Astra SL16xx series AI examples

## Setup Python Environment

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

## Object detection
```bash
python3 -m vision.object_detection 'cam'
```

## Speech-to-text

Moonshine is an edge AI targetted speech-to-text model with Whisper-like Word Error Rate (WER). To transcribe the `jfk.wav`

```bash
python3 -m speech_to_text.moonshine  'samples/jfk.wav'
```

To run live captions with a USB microphones attached (hint: a webcam has a microphone):

```bash
python3 -m speech_to_text.pipeline
```

## Text-to-speech

```bash
python3 -m text_to_speech.piper "synaptics astra example"
```

## Install llama-cpp-python

```bash
Also add sqlite3 binary:
"_sqlite3.cpython-310-aarch64-linux-gnu.so" to astra location "/usr/lib/python3.10/lib-dynload/"
Also add sqllite3 folder:
"sqlite3" folder to astra location "/usr/lib/python3.10/"
```

## Embeddings
```bash
python3 -m embeddings.minilm "synaptics astra example!"
```

## Voice Assistant
```bash
python3 -m voice_assistant.main
```

## LLMs

```bash
python3 -m llm.qwen
python3 -m llm.deepseek
```