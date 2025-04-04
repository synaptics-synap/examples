import sys
from llama_cpp import Llama
from utils.models import download


def run_llm(
    prompt_text="An isosceles trapezoid has an inscribed circle tangent to each of its four sides. The radius of the circle is 3, and the area of the trapezoid is 72. Let the parallel sides of the trapezoid have lengths r and s, with r not equal to s. Find r^2 + s^2.",
):
    model_path = download(
        repo_id="bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        filename="DeepSeek-R1-Distill-Qwen-1.5B-Q6_K.gguf",
    )

    llm = Llama(
        model_path=model_path, verbose=True, n_ctx=8196, n_threads=4, max_tokens=-1
    )

    response_stream = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt_text}], stream=True
    )

    full_response = ""
    for chunk in response_stream:
        token = chunk["choices"][0].get("delta", {}).get("content", "")
        full_response += token
        print(token, end="", flush=True)
    print()

    return full_response


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:])
        run_llm(prompt_text)
    else:
        run_llm()
