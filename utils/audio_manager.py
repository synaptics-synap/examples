import subprocess
import os
import numpy as np


class AudioManager:
    def __init__(self, record_device=None, play_device=None, sample_rate=16000):
        # For recording, we wait until a USB device is available
        self._record_device = record_device or self._get_usb_record_device()
        # For playback, we check if a USB device is available;
        # if not, we warn and set it to None (optional)
        self._play_device = play_device or self._get_usb_play_device()
        self._sample_rate = sample_rate
        self.arecord_process = None

    @property
    def play_device(self):
        """Get the current playback audio device."""
        return self._play_device

    @play_device.setter
    def play_device(self, new_device):
        """Set a new playback audio device."""
        self._play_device = new_device

    @property
    def record_device(self):
        """Get the current recording audio device."""
        return self._record_device

    @record_device.setter
    def record_device(self, new_device):
        """Set a new recording audio device."""
        self._record_device = new_device

    @property
    def sample_rate(self):
        """Get the current sample rate."""
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, new_sample_rate):
        """Set a new sample rate."""
        self._sample_rate = new_sample_rate

    def play(self, filename):
        """Play the audio file using the playback device.

        If no playback device is available, warn and skip audio playback.
        """
        if not self._play_device:
            print("Warning: No playback device available. Skipping audio playback.")
            return
        print(f"Playing through: {self._play_device}")
        subprocess.run(["aplay", "-q", "-D", self._play_device, filename], check=True)

    def start_record(self, chunk_size=512):
        """Start the record process using the recording device."""
        if self.arecord_process:
            self.stop_record()
        command = (
            f"arecord -D {self._record_device} -f S16_LE -r {self._sample_rate} -c 2"
        )
        print(f"Recording from: {self._record_device}")
        print(f"Command: {command}")
        self.arecord_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=chunk_size,
            shell=True,
        )

    def stop_record(self):
        """Stop the record process."""
        if self.arecord_process:
            self.arecord_process.terminate()
            self.arecord_process.wait()
            self.arecord_process = None

    def read(self, chunk_size=512):
        """Read audio data from the record process."""
        if not self.arecord_process:
            raise RuntimeError("Record process not running.")
        while True:
            data = self.arecord_process.stdout.read(chunk_size * 4)
            if not data:
                break
            yield np.frombuffer(data, dtype=np.int16)[::2].astype(np.float32) / 32768.0

    def wait_for_play_audio(self):
        """Wait until a USB playback device is available."""
        print("Waiting for playback audio device...")
        while True:
            process = os.popen("aplay -l | grep USB\\ Audio && sleep 0.5")
            output = process.read()
            process.close()
            if "USB Audio" in output:
                print("Playback device detected:")
                print(output)
                break

    def wait_for_record_audio(self):
        """Wait until a USB record device is available."""
        print("Waiting for record audio device...")
        while True:
            process = os.popen("arecord -l | grep USB\\ Audio && sleep 0.5")
            output = process.read()
            process.close()
            if "USB Audio" in output:
                print("Record device detected:")
                print(output)
                break

    def _get_usb_play_device(self):
        """Find the USB playback device using `aplay -l`."""
        # self.wait_for_play_audio()
        try:
            result = subprocess.run(
                ["aplay", "-l"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "USB Audio" in line:
                    parts = line.split()
                    if parts[0] == "card":
                        card_index = parts[1].rstrip(":")
                    else:
                        continue
                    if "device" in parts:
                        device_pos = parts.index("device")
                        device_index = parts[device_pos + 1].rstrip(":")
                    else:
                        continue
                    device_name = f"plughw:{card_index},{device_index}"
                    print(f"Found playback audio device: {device_name}")
                    return device_name
            print("No USB Audio device found for playback.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error running `aplay -l`: {e}")
            return None

    def _get_usb_record_device(self):
        """Find the USB record device using `arecord -l`."""
        self.wait_for_record_audio()
        try:
            result = subprocess.run(
                ["arecord", "-l"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.splitlines()
            for line in lines:
                if "USB Audio" in line:
                    parts = line.split()
                    if parts[0] == "card":
                        card_index = parts[1].rstrip(":")
                    else:
                        continue
                    if "device" in parts:
                        device_pos = parts.index("device")
                        device_index = parts[device_pos + 1].rstrip(":")
                    else:
                        continue
                    device_name = f"plughw:{card_index},{device_index}"
                    print(f"Found record audio device: {device_name}")
                    return device_name
            print("No USB Audio device found for recording.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error running `arecord -l`: {e}")
            return None
