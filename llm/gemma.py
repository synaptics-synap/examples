from llama_cpp import Llama
from utils.models import download
import time

# Gemma3 1B model
# model_path = download(
#     repo_id="ggml-org/gemma-3-1b-it-GGUF",
#     filename="gemma-3-1b-it-Q8_0.gguf",
# )

# Gemma3 270M model
model_path = download(
    repo_id="ggml-org/gemma-3-270m-it-GGUF",
    filename="gemma-3-270m-it-Q8_0.gguf",
)

print("Loading Gemma 3 model...")
t0 = time.time()
llm = Llama(model_path=model_path, n_ctx=4096, verbose=False)
print(f"Model loaded in {time.time() - t0:.2f} s\n")

# --- Chat memory ---
messages = [{"role": "system", "content": "You are Gemma 3, a concise helpful AI assistant."}]

print("💬 Interactive chat started (type 'exit' or 'quit' to stop)\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        print("Goodbye!")
        break

    messages.append({"role": "user", "content": user_input})

    # --- Streamed response and tokens/sec measurement ---
    print("\nGemma:", end=" ", flush=True)
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

    # --- Store assistant response for context ---
    messages.append({"role": "assistant", "content": output})