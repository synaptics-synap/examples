import os
import json
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import subprocess

from embeddings.minilm import Embeddings

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "qa_pairs.json")


class Agent:
    def __init__(self, qa_file=DATA_PATH):
        self.embeddings = Embeddings()
        with open(qa_file, "r") as f:
            self.qa_pairs = json.load(f)
        self.question_embeddings = self.load_embeddings()

    def load_embeddings(self):
        texts = [pair["question"] for pair in self.qa_pairs]
        embeddings = []
        for text in tqdm(texts, desc="Computing embeddings"):
            embeddings.append(self.embeddings.generate(text))
        return np.array(embeddings)

    def answer_query(self, query):
        query_emb = self.embeddings.generate(query)
        sims = cosine_similarity([query_emb], self.question_embeddings).flatten()
        best_idx = np.argmax(sims)
        return {
            "answer": self.qa_pairs[best_idx]["answer"],
            "similarity": float(sims[best_idx]),
        }


def run_command(command):
    try:
        out = subprocess.check_output(command, shell=True).decode().strip()
    except Exception as e:
        out = f"[error: {e}]"
    return out


def replace_tool_tokens(answer, tools):
    for tool in tools:
        token = tool["token"]
        if token in answer:
            output = run_command(tool["command"])
            answer = answer.replace(token, output)
    return answer


def main():
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    agent = Agent()

    # Load tools from tools.json
    tools_path = os.path.join(os.path.dirname(__file__), "data", "tools.json")
    with open(tools_path, "r") as f:
        tools = json.load(f)

    print(YELLOW + "Assistant ready. Type your question (or 'exit' to quit):" + RESET)
    while True:
        query = input(YELLOW + "> " + RESET)
        if query.lower() in ("exit", "quit"):
            break
        result = agent.answer_query(query)
        answer = result["answer"]
        # Replace tool tokens with command outputs
        answer = replace_tool_tokens(answer, tools)
        similarity = result["similarity"]
        print(YELLOW + "Answer: " + answer + RESET)
        print(YELLOW + "Similarity: " + str(similarity) + RESET)


if __name__ == "__main__":
    main()
