from llama_cpp import Llama
from utils.models import download

model_path = download(
    repo_id="Qwen/Qwen1.5-0.5B-Chat-GGUF",
    filename="qwen1_5-0_5b-chat-q5_k_m.gguf",
)

llm = Llama(model_path=model_path, verbose=False)  # Enable for debug messages

response_stream = llm.create_chat_completion(
    messages=[{"role": "user", "content": "告诉我有关 synaptics Inc 的信息"}],
    stream=True,  # Enable streaming
)

full_response = ""
for chunk in response_stream:
    # Each chunk contains incremental content
    token = chunk["choices"][0].get("delta", {}).get("content", "")
    full_response += token
    print(token, end="", flush=True)

print()
