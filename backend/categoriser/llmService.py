# backend/categoriser/phi3llm.py

import os
from typing import Optional

import requests


class LLMService:
    """
    LLM client that calls an Ollama model instead of loading Phi-3 locally.

    Defaults:
      - base URL: http://localhost:11434
      - model: deepseek-r1:1.5b

    You can override via:
      - OLLAMA_BASE_URL
      - OLLAMA_MODEL
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self.model_name = model_name or os.getenv(
            "OLLAMA_MODEL", "llama3.2"
        )

        print(
            f"Using Ollama model '{self.model_name}' at '{self.base_url}'"
        )

    def predict(self, prompt: str) -> str:
        """
        Generate a prediction from the Ollama model given a prompt.

        Args:
            prompt: The input prompt string.

        Returns:
            The model's text response (stripped).
        """
        url = f"{self.base_url.rstrip('/')}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Keep output short for classification
                "num_predict": 64,
                "temperature": 0.0,
            },
        }

        try:
            resp = requests.post(url, json=payload, timeout=100)
            print("=== DEBUG OLLAMA RAW RESPONSE ===")
            print("Status:", resp.status_code)
            print(resp.text[:500])
            print("=== END DEBUG OLLAMA RAW RESPONSE ===")
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        data = resp.json()
        return (data.get("response") or "").strip()