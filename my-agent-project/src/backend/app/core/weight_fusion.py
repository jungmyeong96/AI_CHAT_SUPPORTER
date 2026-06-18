"""Qdrant weight fusion engine with dept_cd pre-filtering."""

from typing import Any

WEIGHT_MULTIPLIERS: dict[str, float] = {
    "OFFICIAL": 1.5,
    "EXCELLENT": 1.3,
    "GENERAL": 1.0,
}

SELECTED_TYPES = ("OFFICIAL", "EXCELLENT", "GENERAL")


def fuse_score(cosine_score: float, selected_type: str) -> float:
    multiplier = WEIGHT_MULTIPLIERS.get(selected_type, 1.0)
    return round(cosine_score * multiplier, 4)


def pick_top_per_type(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select highest fused_score candidate for each selected_type."""
    best: dict[str, dict[str, Any]] = {}
    for hit in hits:
        payload = hit.get("payload") or {}
        stype = payload.get("selected_type", "GENERAL")
        if stype not in SELECTED_TYPES:
            continue
        cosine = float(hit.get("score", 0.0))
        fused = fuse_score(cosine, stype)
        candidate = {**hit, "cosine_score": cosine, "fused_score": fused}
        if stype not in best or candidate["fused_score"] > best[stype]["fused_score"]:
            best[stype] = candidate

    ordered = []
    for rank, stype in enumerate(SELECTED_TYPES, start=1):
        if stype in best:
            ordered.append({"rank": rank, **best[stype]})
    return ordered


MOCK_RECOMMENDATIONS = [
    {
        "rank": 1,
        "selected_type": "OFFICIAL",
        "weight_multiplier": 1.5,
        "cosine_score": 0.82,
        "fused_score": 1.23,
        "source_id": "d4e5f6a7-b8c9-0123-def0-234567890123",
        "adopted_question": "대출 심사 기준은 무엇인가요?",
        "adopted_answer": (
            "준법감시실 지침에 따르면 LTV 70% 이하, DSR 40% 이하를 준수해야 합니다."
        ),
        "keywords": ["대출", "LTV", "DSR", "준법"],
    },
    {
        "rank": 2,
        "selected_type": "EXCELLENT",
        "weight_multiplier": 1.3,
        "cosine_score": 0.78,
        "fused_score": 1.014,
        "source_id": "e5f6a7b8-c9d0-1234-ef01-345678901234",
        "adopted_question": "여신 심사 시 확인 사항은?",
        "adopted_answer": "소득증빙, 신용등급, 담보평가 3단계를 순차 확인합니다.",
        "keywords": ["여신", "소득증빙", "신용등급"],
    },
    {
        "rank": 3,
        "selected_type": "GENERAL",
        "weight_multiplier": 1.0,
        "cosine_score": 0.71,
        "fused_score": 0.71,
        "source_id": "f6a7b8c9-d0e1-2345-f012-456789012345",
        "adopted_question": "고객 대출 문의 응대 방법",
        "adopted_answer": (
            "내부 FAQ 시스템에서 유사 사례를 검색 후 담당자에게 에스컬레이션합니다."
        ),
        "keywords": ["FAQ", "에스컬레이션"],
    },
]
