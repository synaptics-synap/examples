# Granite Embeddings 107M parameter dense biencoder embedding model that can be used to generate high quality text embeddings.
# Supports English Chinese Arabic Czech German Spanish French Italian Japanese Korean Dutch Portuguese 
import sys
from llama_cpp import Llama
from utils.models import download


class Embeddings:
    def __init__(self):
        self.model_path = download(
            repo_id="bartowski/granite-embedding-107m-multilingual-GGUF",
            filename="granite-embedding-107m-multilingual-Q8_0.gguf",
        )

        self.llm = Llama(
            model_path=self.model_path,
            n_threads=4,
            n_ctx=128,
            n_batch=512,
            embedding=True,
            verbose=False,  # Set verbose to False to keep llm quiet
        )

    def generate(self, text):
        try:
            embedding = self.llm.embed(text)
            if embedding is None:
                raise ValueError("No embedding returned")
            return embedding
        except Exception as e:
            print("Error generating embedding:", e)
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python script.py "text to embed"')
        sys.exit(1)

    input_text = sys.argv[1]
    generator = Embeddings()
    embedding = generator.generate(input_text)
    print("Generated Embedding:", embedding)
