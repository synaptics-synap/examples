import os
import sys
import argparse
import hashlib
from utils.models import download


class TextToSpeech:
    def __init__(self, voice="en_US-lessac-low", output_dir="output"):
        # Voice must be in the format LOCALE-VOICENAME-STYLE, e.g. en_US-lessac-low
        parts = voice.split("-")
        if len(parts) != 3:
            raise ValueError(
                "Voice must be in format LOCALE-VOICENAME-STYLE, e.g. en_US-lessac-low"
            )
        locale, voice_name, style = parts
        short_lang = locale.split("_")[0] if "_" in locale else locale[:2].lower()
        onnx_file_path = f"{short_lang}/{locale}/{voice_name}/{style}/{voice}.onnx"
        json_file_path = f"{short_lang}/{locale}/{voice_name}/{style}/{voice}.onnx.json"
        self.onnx_file = download(
            repo_id="rhasspy/piper-voices", filename=onnx_file_path
        )
        self.json_file = download(
            repo_id="rhasspy/piper-voices", filename=json_file_path
        )
        self.output_dir = os.path.join(os.path.dirname(__file__), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def file_checksum(content: str, hash_length: int = 16) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:hash_length]

    def synthesize(self, text: str, output_filename: str = None) -> str:
        if output_filename is None:
            chk = self.file_checksum(text + self.onnx_file)
            output_filename = os.path.join(self.output_dir, f"speech-output-{chk}.wav")

        if os.path.exists(output_filename):
            return output_filename

        cmd = f'echo "{text}" | piper --model {self.onnx_file} --output_file {output_filename}'
        os.system(cmd)
        return output_filename


def main():
    parser = argparse.ArgumentParser(
        description="Piper Text-to-Speech command line tool."
    )
    parser.add_argument("text", type=str, help="Text to convert to speech")
    parser.add_argument(
        "-v",
        "--voice",
        type=str,
        default="en_US-lessac-low",
        help="Voice in format LOCALE-VOICENAME-STYLE (default: en_US-lessac-low)",
    )
    args = parser.parse_args()

    tts = TextToSpeech(voice=args.voice)
    wav_path = tts.synthesize(args.text)
    print(f"Audio written to: {wav_path}")


if __name__ == "__main__":
    main()
