"""AI recommendation routes (F3, F4)."""

import asyncio
import time
import uuid
from datetime import date

from fastapi import APIRouter, HTTPException

from app.core.ollama_client import generate_keywords, get_embedding
from app.core.qdrant_engine import COLLECTION, prepare_recommendations, upsert_knowledge
from app.core.ollama_client import VECTOR_SIZE
from app.database import get_connection
from app.schemas import (
    AdoptPayload,
    RecommendAdoptRequest,
    RecommendAdoptResponse,
    RecommendPrepareRequest,
    RecommendPrepareResponse,
    RecommendationItem,
)

router = APIRouter(prefix="/ai/recommend", tags=["AI Recommend"])


def _fetch_chat_context(chat_id: str, room_id: str, emp_id: str) -> tuple[str, str, str]:
    with get_connection() as conn:
        row = conn.execute(
            """SELECT h.MESSAGE, u.DEPT_CD, u.DEPT_NAME
               FROM CHAT_HISTORY h
               JOIN USER_DEPT u ON h.EMP_ID = u.EMP_ID
               WHERE h.CHAT_ID = ? AND h.ROOM_ID = ? AND h.USED_YN = 1""",
            (chat_id, room_id),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Chat not found: {chat_id}")

        prior = conn.execute(
            """SELECT MESSAGE FROM CHAT_HISTORY
               WHERE ROOM_ID = ? AND USED_YN = 1 AND CHAT_ID != ?
               ORDER BY CREATED_TM DESC LIMIT 3""",
            (room_id, chat_id),
        ).fetchall()
        context = " ".join(r["MESSAGE"] for r in reversed(prior))
        context = f"{context} {row['MESSAGE']}".strip()
        dept_cd = row["DEPT_CD"] or ""
        return context, dept_cd, row["DEPT_NAME"]


@router.post("/prepare", response_model=RecommendPrepareResponse)
async def recommend_prepare(body: RecommendPrepareRequest) -> RecommendPrepareResponse:
    context, dept_cd, _ = await asyncio.to_thread(
        _fetch_chat_context, body.chat_id, body.room_id, body.emp_id
    )
    keywords = await generate_keywords(context)
    recs_raw = await prepare_recommendations(context, dept_cd)

    recommendations = [RecommendationItem(**r) for r in recs_raw]
    return RecommendPrepareResponse(
        chat_id=body.chat_id,
        room_id=body.room_id,
        emp_id=body.emp_id,
        dept_cd=dept_cd,
        refined_keywords=keywords,
        recommendations=recommendations,
    )


@router.post("/adopt", response_model=RecommendAdoptResponse, status_code=201)
async def recommend_adopt(body: RecommendAdoptRequest) -> RecommendAdoptResponse:
    adopt_id = str(uuid.uuid4())
    today = date.today().isoformat()
    created_tm = int(time.time())

    def _resolve_dept() -> str:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT DEPT_CD FROM USER_DEPT WHERE EMP_ID = ?", (body.emp_id,)
            ).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Invalid emp_id")
            return row["DEPT_CD"] or ""

    dept_cd = await asyncio.to_thread(_resolve_dept)
    embed_text = f"{body.adopted_question} {body.adopted_answer}"
    vector = await get_embedding(embed_text)

    payload = {
        "chat_id": body.chat_id,
        "emp_id": body.emp_id,
        "dept_cd": dept_cd,
        "adopted_question": body.adopted_question,
        "adopted_answer": body.adopted_answer,
        "keywords": body.keywords,
        "selected_type": body.selected_type,
        "weight_score": body.weight_score,
        "created_at": today,
        "created_tm": created_tm,
    }

    success = await upsert_knowledge(adopt_id, vector, payload)
    if not success:
        raise HTTPException(status_code=502, detail="Qdrant upsert failed")

    return RecommendAdoptResponse(
        adopt_id=adopt_id,
        qdrant_upsert_status="success",
        collection=COLLECTION,
        vector_size=VECTOR_SIZE,
        payload=AdoptPayload(**payload),
    )
