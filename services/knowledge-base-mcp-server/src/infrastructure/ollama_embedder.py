"""Embedder adapter backed by an Ollama embeddings endpoint."""
import httpx


class OllamaEmbedder:
    def __init__(self, base_url: str, model: str, timeout: float = 60.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        with httpx.Client(base_url=self._base_url, timeout=self._timeout) as client:
            for text in texts:
                response = client.post(
                    "/api/embeddings", json={"model": self._model, "prompt": text}
                )
                response.raise_for_status()
                vectors.append(response.json()["embedding"])
        return vectors
