import json
import os
import sys
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from embeddings.multilingual import Embeddings

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "qa_pairs.json")


class Agent:
    def __init__(self, qa_file=DEFAULT_PATH):
        self.embeddings = Embeddings()
        with open(qa_file, "r") as f:
            self.qa_pairs = json.load(f)
        self.question_embeddings = self.load_embeddings()

    def load_embeddings(self):
        texts = [pair["question"] + " " + pair["answer"] for pair in self.qa_pairs]
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        qa_file = sys.argv[1]
    else:
        qa_file = DEFAULT_PATH

    YELLOW = "\033[93m"
    RESET = "\033[0m"
    agent = Agent(qa_file=qa_file)
    print(YELLOW + "Assistant ready. Type your question (or 'exit' to quit):" + RESET)
    while True:
        query = input(YELLOW + "> " + RESET)
        if query.lower() in ("exit", "quit"):
            break
        result = agent.answer_query(query)
        print(YELLOW + "Answer: " + result["answer"] + RESET)
        print(YELLOW + "Similarity: " + str(result["similarity"]) + RESET)
