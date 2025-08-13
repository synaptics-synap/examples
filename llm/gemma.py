from llama_cpp import Llama
from utils.models import download

model_path = download(
    repo_id="ggml-org/gemma-3-1b-it-GGUF",
    filename="gemma-3-1b-it-Q8_0.gguf",
)
llm = Llama(model_path=model_path, verbose=False)   

messages = []
print("Interactive chat. Type 'exit' to quit.")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ("exit", "quit"):
        break
    messages.append({"role": "user", "content": user_input})
    response_stream = llm.create_chat_completion(
        messages=messages,
        stream=True,
        # max_tokens=128,  # shorter answers
        temperature=0.7,  
    )
    full_response = ""
    for chunk in response_stream:
        token = chunk["choices"][0].get("delta", {}).get("content", "")
        full_response += token
        print(token, end="", flush=True)
    print()
    messages.append({"role": "assistant", "content": full_response})
