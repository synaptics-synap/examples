import subprocess
import os
import numpy as np


class AudioManager:
    def __init__(self, record_device=None, play_device=None, sample_rate=16000):
        self._sample_rate = sample_rate
        self.arecord_process = None

        self._astra_version = self._get_astra_version()
        self._audio_config = self._get_asoundrc_device()

        self._play_device = play_device or self._get_usb_play_device()
        self._record_device = record_device or self._get_usb_record_device()

        self._print_final_device_info()
 
 
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
        # print(f"Recording from: {self._record_device}")
        # print(f"Command: {command}")
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
 
    
    def _get_astra_version(self):
        try:
            with open("/etc/astra_version", "r") as f:
                return f.read().strip()
        except Exception:
            return ""

    def _print_final_device_info(self):
        def get_card_info(card_index):
            try:
                output = subprocess.check_output("arecord -l", shell=True, text=True)
                for line in output.splitlines():
                    if f"card {card_index}:" in line:
                        return line.strip()
            except Exception:
                return None
            return None

        # Safely normalize devices
        record_hw = self._record_device.replace("plughw:", "").replace("hw:", "") if self._record_device else None
        playback_hw = (
            self._audio_config.get("asoundrc_device")
            if self._audio_config.get("asoundrc_device")
            else self._play_device.replace("plughw:", "").replace("hw:", "")
            if self._play_device else None
        )

        # Plugplay fallback
        if self._record_device == "plugplay":
            record_hw = self._audio_config.get("asoundrc_device", None)

        # Get card numbers
        record_card = record_hw.split(",")[0] if record_hw and "," in record_hw else None
        playback_card = playback_hw.split(",")[0] if playback_hw and "," in playback_hw else None

        # Resolve names
        rec_info = get_card_info(record_card) if record_card else "No recording device"
        play_info = get_card_info(playback_card) if playback_card else "No playback device"

        # Output
        print(f"Recording device : hw:{record_hw or 'None'} - {rec_info}")
        print(f"Playback device  : hw:{playback_hw or 'None'} - {play_info}")


    def _get_asoundrc_device(self):
        result = {
            "asoundrc_device": None,
            "playback_devices": [],
            "capture_devices": [],
        }

        try:
            pcm_output = subprocess.check_output("cat /proc/asound/pcm", shell=True, text=True)
            for line in pcm_output.splitlines():
                if "usb" in line.lower() and "audio" in line.lower():
                    hw_id = line.split(":")[0].strip()
                    card, dev = [str(int(x)) for x in hw_id.split("-")]
                    name = line.split(":")[1].strip().split()[0]

                    if "playback" in line:
                        result["playback_devices"].append((card, dev, name))
                    if "capture" in line:
                        result["capture_devices"].append((card, dev, name))

        except Exception as e:
            print(f"Error reading /proc/asound/pcm: {e}")

        # Only create .asoundrc if SDK version is 1.6.0
        if self._astra_version == "1.6.0":
            for card, dev, _ in result["playback_devices"]:
                if (card, dev) in [(c, d) for c, d, _ in result["capture_devices"]]:
                    result["asoundrc_device"] = f"{card},{dev}"
                    asoundrc_content = f"""
pcm.plugplay {{
    type plug
    slave {{
        pcm "hw:{card},{dev}"
        period_size 1024
        buffer_size 2048
    }}
}}
"""
                    try:
                        asoundrc_path = os.path.expanduser("~/.asoundrc")
                        with open(asoundrc_path, "w") as f:
                            f.write(asoundrc_content.strip() + "\n")
                            print(f"Astra SDK {self._astra_version} found, .asoundrc created with hw:{card},{dev}")
                    except Exception as e:
                        print(f"Error writing .asoundrc: {e}")
                    break

        return result


    def _get_usb_record_device(self):
        capture = self._audio_config["capture_devices"]
        asoundrc_device = self._audio_config["asoundrc_device"]

        # Add this line: fallback detection of playback_hw for non-1.6 SDKs
        playback_hw = asoundrc_device or (
            self._play_device.replace("plughw:", "").replace("hw:", "") if self._play_device else None
        )

        # Try to avoid using the same device for record and playback
        for card, dev, name in capture:
            if f"{card},{dev}" != playback_hw:
                if self._astra_version == "1.6.0":
                    return f"hw:{card},{dev}"
                else:
                    return f"plughw:{card},{dev}"

        # Fallback: use shared device
        if self._astra_version == "1.6.0" and asoundrc_device:
            print(f"No separate mic found. Using shared plugplay (hw:{asoundrc_device})")
            return "plugplay"

        if capture:
            card, dev, name = capture[0]
            print(f"No separate mic found. Using shared device for recording: {name} (plughw:{card},{dev})")
            return f"plughw:{card},{dev}"

        print("No USB mic available")
        return None


    def _get_usb_play_device(self):
        if self._astra_version == "1.6.0":
            return "plugplay" if self._audio_config["asoundrc_device"] else None

        playback = self._audio_config["playback_devices"]
        if playback:
            card, dev, name = playback[0]
            print(f"Selected speaker: {name} (plughw:{card},{dev})")
            return f"plughw:{card},{dev}"

        print("No USB speaker/playback device available")
        return None

