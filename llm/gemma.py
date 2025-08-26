from llama_cpp import Llama
from utils.models import download

# Gemma3 1B model
# model_path = download(
#     repo_id="ggml-org/gemma-3-1b-it-GGUF",
#     filename="gemma-3-1b-it-Q8_0.gguf",
# )

# Gemma3 270M model
model_path = download(
    repo_id="ggml-org/gemma-3-270m-GGUF",
    filename="gemma-3-270m-Q8_0.gguf",
)
llm = Llama(model_path=model_path, verbose=False)   

messages = []
print("Interactive chat. Type 'exit' to quit.")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ("exit", "quit"):
        break
    # Only send the current user message, no history
    current_messages = [{"role": "user", "content": user_input}]
    response_stream = llm.create_chat_completion(
        messages=current_messages,
        stream=True,
        #max_tokens=128,  # shorter answers, avoid context overflow
        temperature=0.7,  
    )
    full_response = ""
    for chunk in response_stream:
        token = chunk["choices"][0].get("delta", {}).get("content", "")
        full_response += token
        print(token, end="", flush=True)
    print()
    messages.append({"role": "assistant", "content": full_response})
