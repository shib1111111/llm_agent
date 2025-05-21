from langchain.llms.base import LLM
from langchain_core.embeddings import Embeddings
import requests
import json
from typing import List, Optional
from pydantic import BaseModel, Field

from config import CONFIG

class BedrockLanguageModelConfig(BaseModel):
    api_key: str = Field(..., description="API key for Bedrock service")
    model_id: str = Field(default="claude-3.5-sonnet", description="Model ID for the language model")
    url: str = Field(default="https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/", description="API endpoint URL")

class BedrockLanguageModel(LLM, BedrockLanguageModelConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        payload = {
            "api_key": self.api_key,
            "prompt": prompt,
            "model_id": kwargs.get("model_id", self.model_id),
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        return result["response"]["content"][0]["text"]

    @property
    def _llm_type(self) -> str:
        return "bedrock_language_model"

class BedrockEmbeddingsConfig(BaseModel):
    api_key: str = Field(..., description="API key for Bedrock service")
    model_id: str = Field(default="amazon-embedding-v2", description="Model ID for embeddings")
    url: str = Field(default="https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/", description="API endpoint URL")

class BedrockEmbeddings(Embeddings, BedrockEmbeddingsConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text input."""
        payload = {
            "api_key": self.api_key,
            "prompt": text,
            "model_id": self.model_id
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            return result["response"]["embedding"]
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error generating embedding: {str(e)}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text inputs."""
        return [self.embed_query(text) for text in texts]

    @property
    def _llm_type(self) -> str:
        return "bedrock_embeddings"

# Example usage
if __name__ == "__main__":
    # Initialize the language model with a specific model ID
    llm = BedrockLanguageModel(api_key=CONFIG["ANTHROPIC_API_KEY"], model_id="claude-3.5-sonnet")

    # Generate a response
    response = llm.invoke("Write a short story about a robot who discovers music.")
    print("Story Response:")
    print(response)

    # Initialize the embeddings class with a specific model ID
    embeddings = BedrockEmbeddings(api_key=CONFIG["ANTHROPIC_API_KEY"], model_id="amazon-embedding-v2")

    # Single text embedding
    text = "The quick brown fox jumps over the lazy dog."
    embedding_vector = embeddings.embed_query(text)
    print(f"\nSingle Text Embedding:")
    print(f"Embedding dimension: {len(embedding_vector)}")
    print(f"Embedding vector (first 5 values): {embedding_vector[:5]}...")

    # Multiple text embeddings
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "A robot discovers the beauty of music."
    ]
    embedding_vectors = embeddings.embed_documents(texts)
    print("\nMultiple Text Embeddings:")
    for i, vec in enumerate(embedding_vectors):
        print(f"Text {i+1} embedding dimension: {len(vec)}")
        print(f"Text {i+1} embedding (first 5 values): {vec[:5]}...")