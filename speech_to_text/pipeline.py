import time
import os
import numpy as np
from scipy.io.wavfile import write

from silero_vad import VADIterator, load_silero_vad
from speech_to_text.moonshine import SpeechToText
from utils.audio_manager import AudioManager

SAMPLING_RATE = 16000
CHUNK_SIZE = 512
LOOKBACK_CHUNKS = 7
MAX_LINE_LENGTH = 80
MAX_SPEECH_SECS = 15
MIN_REFRESH_SECS = 0.5

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "input.wav")


class SpeechToTextPipeline:
    def __init__(self, model, handler, echo=False):
        self.model = model
        self.handler = handler
        self.echo = echo

        self.speech_to_text = SpeechToText(model=model, rate=SAMPLING_RATE)
        self.vad_model = load_silero_vad(onnx=True)
        self.vad_iterator = VADIterator(
            model=self.vad_model,
            sampling_rate=SAMPLING_RATE,
            threshold=0.3,
            min_silence_duration_ms=300,
        )

        self.audio_manager = AudioManager()
        self.caption_cache = []
        self.lookback_size = LOOKBACK_CHUNKS * CHUNK_SIZE
        self.speech = np.empty(0, dtype=np.float32)
        self.recording = False

    def print_captions(self, text):
        if len(text) < MAX_LINE_LENGTH:
            for cap in self.caption_cache[::-1]:
                text = cap + " " + text
                if len(text) > MAX_LINE_LENGTH:
                    break
        if len(text) > MAX_LINE_LENGTH:
            text = text[-MAX_LINE_LENGTH:]
        print("\r" + (" " * MAX_LINE_LENGTH) + "\r" + text, end="", flush=True)

    def soft_reset(self):
        self.vad_iterator.triggered = False
        self.vad_iterator.temp_end = 0
        self.vad_iterator.current_sample = 0

    def end_recording(self, do_print=True):
        start_inference = time.time()
        text = self.speech_to_text.transcribe(self.speech)
        inference_time = time.time() - start_inference

        if text.strip():
            self.handler(text, inference_time)

        max_val = np.max(np.abs(self.speech))
        if max_val != 0:
            scaled = np.int16(self.speech / max_val * 32767)
        else:
            scaled = np.int16(self.speech)
        write(OUTPUT_FILE, SAMPLING_RATE, scaled)

        if self.echo:
            self.audio_manager.play(OUTPUT_FILE)

        self.speech *= 0.0

    def run(self):
        try:
            self.audio_manager.start_record(chunk_size=CHUNK_SIZE)
            print("Press Ctrl+C to quit speech-to-text.\n")
            start_time = time.time()
            call_end_recording = False

            for chunk in self.audio_manager.read(chunk_size=CHUNK_SIZE):
                if call_end_recording:
                    self.end_recording()
                    call_end_recording = False

                self.speech = np.concatenate((self.speech, chunk))
                if not self.recording:
                    self.speech = self.speech[-self.lookback_size :]
                speech_dict = self.vad_iterator(chunk)

                if speech_dict:
                    if "start" in speech_dict and not self.recording:
                        self.recording = True
                        start_time = time.time()
                    if "end" in speech_dict and self.recording:
                        call_end_recording = True
                        self.recording = False
                elif self.recording:
                    if (len(self.speech) / SAMPLING_RATE) > MAX_SPEECH_SECS:
                        call_end_recording = True
                        self.recording = False
                        self.soft_reset()
                    elif (time.time() - start_time) > MIN_REFRESH_SECS:
                        start_time = time.time()
        except KeyboardInterrupt:
            print("\n Speech-to-text stopped by user.")
            self.audio_manager.stop_record()


if __name__ == "__main__":
    # Example usage:
    def handle_results(text, inference_time):
        if text:
            print(f"\033[93mSTT: {text} \033[92m({inference_time*1000:.0f}ms)\033[0m")

    pipe = SpeechToTextPipeline(
        model="base",  # Set to "tiny" for faster but less accurate model
        handler=handle_results,
        echo=False,  # Set echo True to play audio after recording ends for debug purposes
    )

    pipe.run()
