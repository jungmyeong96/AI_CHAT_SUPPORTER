"""Ollama REST client (single-thread friendly)."""

import os
from typing import Any

import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
GEN_MODEL = os.getenv("OLLAMA_GEN_MODEL", "llama3.2:3b")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "768"))


async def generate_keywords(context: str) -> list[str]:
    prompt = (
        "Extract 3-5 Korean search keywords from this chat context. "
        "Return comma-separated keywords only.\n\n"
        f"{context}"
    )
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": GEN_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            text = resp.json().get("response", "")
            keywords = [k.strip() for k in text.replace("\n", ",").split(",") if k.strip()]
            return keywords[:5] if keywords else _fallback_keywords(context)
    except Exception:
        return _fallback_keywords(context)


def _fallback_keywords(context: str) -> list[str]:
    tokens = [t for t in context.replace(",", " ").split() if len(t) >= 2]
    return tokens[:4] or ["업무", "문의"]


async def get_embedding(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            vector = data.get("embedding", [])
            if vector:
                return _normalize_vector(vector)
    except Exception:
        pass
    return _hash_embedding(text)


def _normalize_vector(vector: list[float]) -> list[float]:
    if len(vector) >= VECTOR_SIZE:
        return vector[:VECTOR_SIZE]
    return vector + [0.0] * (VECTOR_SIZE - len(vector))


def _hash_embedding(text: str) -> list[float]:
    """Deterministic lightweight fallback when Ollama is unavailable."""
    import hashlib
    import math

    seed = hashlib.sha256(text.encode()).digest()
    values = []
    for i in range(VECTOR_SIZE):
        b = seed[i % len(seed)]
        values.append((b / 255.0) * 2 - 1)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]
