import sys
import time
import json
import numpy as np
import onnxruntime
import soundfile as sf
from utils.models import download
from tokenizers import Tokenizer


class SpeechToText:
    def __init__(self, model="base", onnx_repo="UsefulSensors/moonshine", rate=16000):
        self.config_repo = f"UsefulSensors/moonshine-{model}"
        self.rate = rate
        self.config = self._load_config()
        self.tokenizer = self._load_tokenizer()
        encoder_path = download(
            repo_id=onnx_repo,
            filename=f"onnx/merged/{model}/quantized/encoder_model.onnx",
        )
        decoder_path = download(
            repo_id=onnx_repo,
            filename=f"onnx/merged/{model}/quantized/decoder_model_merged.onnx",
        )
        self.encoder_session = onnxruntime.InferenceSession(encoder_path)
        self.decoder_session = onnxruntime.InferenceSession(decoder_path)
        self.eos_token_id = self.config["eos_token_id"]
        self.decoder_start_token_id = self.config["decoder_start_token_id"]
        self.num_key_value_heads = self.config["decoder_num_key_value_heads"]
        self.dim_kv = (
            self.config["hidden_size"] // self.config["decoder_num_attention_heads"]
        )
        self.decoder_layers = self.config["decoder_num_hidden_layers"]
        self.max_len = self.config["max_position_embeddings"]
        self.transcribe(np.zeros(rate, dtype=np.float32))

    def _load_config(self):
        path = download(repo_id=self.config_repo, filename="config.json")
        with open(path, "r") as f:
            return json.load(f)

    def _load_tokenizer(self):
        path = download(repo_id=self.config_repo, filename="tokenizer.json")
        return Tokenizer.from_file(path)

    def _generate(self, audio, max_len=None):
        if max_len is None:
            max_len = min((audio.shape[-1] // self.rate) * 6, self.max_len)
        enc_out = self.encoder_session.run(None, {"input_values": audio})[0]
        batch_size = enc_out.shape[0]
        input_ids = np.array(
            [[self.decoder_start_token_id]] * batch_size, dtype=np.int64
        )
        past_kv = {
            f"past_key_values.{layer}.{mod}.{kv}": np.zeros(
                [batch_size, self.num_key_value_heads, 0, self.dim_kv], dtype=np.float32
            )
            for layer in range(self.decoder_layers)
            for mod in ("decoder", "encoder")
            for kv in ("key", "value")
        }
        gen_tokens = input_ids
        for i in range(max_len):
            use_cache_branch = i > 0
            dec_inputs = {
                "input_ids": gen_tokens[:, -1:],
                "encoder_hidden_states": enc_out,
                "use_cache_branch": [use_cache_branch],
                **past_kv,
            }
            out = self.decoder_session.run(None, dec_inputs)
            logits = out[0]
            present_kv = out[1:]
            next_tokens = logits[:, -1].argmax(axis=-1, keepdims=True)
            for j, key in enumerate(past_kv):
                if not use_cache_branch or "decoder" in key:
                    past_kv[key] = present_kv[j]
            gen_tokens = np.concatenate([gen_tokens, next_tokens], axis=-1)
            if (next_tokens == self.eos_token_id).all():
                break
        return gen_tokens

    def transcribe(self, speech):
        speech = speech.astype(np.float32)[np.newaxis, :]
        tokens = self._generate(speech)
        return self.tokenizer.decode_batch(tokens, skip_special_tokens=True)[0]


def main():
    if len(sys.argv) < 2:
        print("Usage: python speech_to_text.py <audio_file>")
        sys.exit(1)
    audio_path = sys.argv[1]
    data, sr = sf.read(audio_path, dtype="float32")
    print("Loading Moonshine model using ONNX runtime ...")
    stt = SpeechToText()
    audio_ms = len(data) / sr * 1000
    print("Transcribing ...")
    start = time.time()
    text = stt.transcribe(data)
    end = time.time()
    transcribe_ms = (end - start) * 1000
    speed_factor = (audio_ms / 1000) / (end - start)
    print(f"audio sample time: {int(audio_ms)}ms")
    print(f"transcribe time:  {int(transcribe_ms)}ms")
    print(f"speed: {speed_factor:.1f}x")
    print(f"result: {text}")


if __name__ == "__main__":
    main()
