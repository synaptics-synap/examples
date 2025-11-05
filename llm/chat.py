import sys
import time
from llama_cpp import Llama
import requests
import os
from huggingface_hub import hf_hub_download

# Model options
MODELS = {
    "gemma": {
        "repo_id": "ggml-org/gemma-3-270m-it-GGUF",
        "filename": "gemma-3-270m-it-Q8_0.gguf",
    },
    "qwen": {
        "repo_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "filename": "qwen2.5-0.5b-instruct-q8_0.gguf",
    }
}

if len(sys.argv) < 2:
    model_key = "gemma"
else:
    model_key = sys.argv[1]
    if model_key not in MODELS:
        print("Usage: python chat.py <model>")
        print("Available models:", ", ".join(MODELS.keys()))
        sys.exit(1)

model_info = MODELS[model_key]
model_path = hf_hub_download(repo_id=model_info["repo_id"], filename=model_info["filename"], cache_dir="models")

print(f"Loading {model_key} model...")
t0 = time.time()
llm = Llama(model_path=model_path, n_ctx=4096, verbose=False)
print(f"Model loaded in {time.time() - t0:.2f} s\n")
messages = [{"role": "system", "content": "You are a concise helpful AI assistant."}]
print("\U0001F4AC Interactive chat started (type 'exit' or 'quit' to stop)\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break
    messages.append({"role": "user", "content": user_input})
    print(f"\n{model_key.capitalize()}:", end=" ", flush=True)
    output = ""
    t1 = time.time()
    token_count = 0
    for chunk in llm.create_chat_completion(messages=messages, stream=True, max_tokens=256, temperature=0.7):
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            text = delta["content"]
            output += text
            print(text, end="", flush=True)
            token_count += 1
    print()
    total_time = time.time() - t1
    tps = token_count / total_time if token_count and total_time > 0 else 0.0
    print(f"\nAvg tokens/sec: {tps:.2f}\n")
    messages.append({"role": "assistant", "content": output})