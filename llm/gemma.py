from llama_cpp import Llama
from utils.models import download

model_path = download(
    repo_id="unsloth/gemma-3-1b-it-GGUF",
    filename="gemma-3-1b-it-BF16.gguf",
)

llm = Llama(model_path=model_path, verbose=False)  # Enable for debug messages

response_stream = llm.create_chat_completion(
    messages=[
        {"role": "user", "content": "Tell me briefly about the benefits of Edge AI"}
    ],
    stream=True,  # Enable streaming
)

full_response = ""
for chunk in response_stream:
    # Each chunk contains incremental content
    token = chunk["choices"][0].get("delta", {}).get("content", "")
    full_response += token
    print(token, end="", flush=True)

print()
