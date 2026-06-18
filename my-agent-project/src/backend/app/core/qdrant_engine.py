"""Qdrant HTTP client via httpx (approved package)."""

import os
import uuid
from typing import Any

import httpx

from app.core.ollama_client import VECTOR_SIZE, get_embedding
from app.core.weight_fusion import MOCK_RECOMMENDATIONS, WEIGHT_MULTIPLIERS, pick_top_per_type

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION = "adopted_knowledge"


async def ensure_collection() -> None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{QDRANT_URL}/collections/{COLLECTION}")
            if resp.status_code == 200:
                return
            await client.put(
                f"{QDRANT_URL}/collections/{COLLECTION}",
                json={
                    "vectors": {
                        "size": VECTOR_SIZE,
                        "distance": "Cosine",
                        "on_disk": True,
                    }
                },
            )
    except Exception:
        pass


async def search_knowledge(vector: list[float], dept_cd: str, limit: int = 20) -> list[dict[str, Any]]:
    body: dict[str, Any] = {
        "vector": vector,
        "limit": limit,
        "with_payload": True,
        "score_threshold": 0.0,
    }
    if dept_cd:
        body["filter"] = {
            "must": [{"key": "dept_cd", "match": {"value": dept_cd}}]
        }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
                json=body,
            )
            resp.raise_for_status()
            return resp.json().get("result", [])
    except Exception:
        return []


async def upsert_knowledge(
    adopt_id: str,
    vector: list[float],
    payload: dict[str, Any],
) -> bool:
    point = {"id": adopt_id, "vector": vector, "payload": payload}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.put(
                f"{QDRANT_URL}/collections/{COLLECTION}/points",
                json={"points": [point]},
            )
            resp.raise_for_status()
            return True
    except Exception:
        return False


def hits_to_recommendations(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked = pick_top_per_type(hits)
    results = []
    for item in picked:
        payload = item.get("payload") or {}
        stype = payload.get("selected_type", "GENERAL")
        results.append(
            {
                "rank": item["rank"],
                "selected_type": stype,
                "weight_multiplier": WEIGHT_MULTIPLIERS.get(stype, 1.0),
                "cosine_score": item["cosine_score"],
                "fused_score": item["fused_score"],
                "source_id": str(item.get("id", uuid.uuid4())),
                "adopted_question": payload.get("adopted_question", ""),
                "adopted_answer": payload.get("adopted_answer", ""),
                "keywords": payload.get("keywords", []),
            }
        )
    return results


async def prepare_recommendations(query_text: str, dept_cd: str) -> list[dict[str, Any]]:
    vector = await get_embedding(query_text)
    hits = await search_knowledge(vector, dept_cd)
    recs = hits_to_recommendations(hits)
    if len(recs) >= 3:
        return recs[:3]

    existing_types = {r["selected_type"] for r in recs}
    for mock in MOCK_RECOMMENDATIONS:
        if mock["selected_type"] not in existing_types:
            recs.append(mock)
            existing_types.add(mock["selected_type"])
        if len(recs) >= 3:
            break

    while len(recs) < 3:
        recs.append(MOCK_RECOMMENDATIONS[len(recs) % 3])

    for i, rec in enumerate(recs[:3], start=1):
        rec["rank"] = i
    return recs[:3]
