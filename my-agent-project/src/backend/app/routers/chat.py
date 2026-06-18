"""Chat management routes (F1, F2)."""

import asyncio
import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.core.compliance import is_closing_message, mask_message
from app.database import get_connection
from app.schemas import (
    ChatHistoryResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    HistoryMessageItem,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


@router.get("/rooms/{room_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    room_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> ChatHistoryResponse:
    def _query() -> ChatHistoryResponse:
        with get_connection() as conn:
            room = conn.execute(
                "SELECT ROOM_ID FROM CHAT_ROOM WHERE ROOM_ID = ?", (room_id,)
            ).fetchone()
            if not room:
                raise HTTPException(status_code=404, detail=f"Room not found: {room_id}")

            total = conn.execute(
                """SELECT COUNT(*) FROM CHAT_HISTORY
                   WHERE ROOM_ID = ? AND USED_YN = 1""",
                (room_id,),
            ).fetchone()[0]

            rows = conn.execute(
                """SELECT h.CHAT_ID, h.ROOM_ID, h.EMP_ID, u.EMP_NAME, u.DEPT_NAME,
                          h.MESSAGE, h.USED_YN, h.COMPLIANCE_YN, h.CREATED_AT, h.CREATED_TM
                   FROM CHAT_HISTORY h
                   JOIN USER_DEPT u ON h.EMP_ID = u.EMP_ID
                   WHERE h.ROOM_ID = ? AND h.USED_YN = 1
                   ORDER BY h.CREATED_TM ASC
                   LIMIT ? OFFSET ?""",
                (room_id, limit, offset),
            ).fetchall()

            messages = [
                HistoryMessageItem(
                    chat_id=r["CHAT_ID"],
                    room_id=r["ROOM_ID"],
                    emp_id=r["EMP_ID"],
                    emp_name=r["EMP_NAME"],
                    dept_name=r["DEPT_NAME"],
                    message=r["MESSAGE"],
                    used_yn=r["USED_YN"],
                    compliance_yn=r["COMPLIANCE_YN"],
                    created_at=r["CREATED_AT"],
                    created_tm=r["CREATED_TM"],
                )
                for r in rows
            ]
            return ChatHistoryResponse(room_id=room_id, total_count=total, messages=messages)

    return await asyncio.to_thread(_query)


@router.post("/message", response_model=ChatMessageResponse, status_code=201)
async def create_chat_message(body: ChatMessageCreate) -> ChatMessageResponse:
    masked, compliance_yn = mask_message(body.message)
    chat_id = str(uuid.uuid4())
    today = date.today().isoformat()
    created_tm = _now_iso()

    def _insert() -> ChatMessageResponse:
        with get_connection() as conn:
            room = conn.execute(
                "SELECT ROOM_ID FROM CHAT_ROOM WHERE ROOM_ID = ?", (body.room_id,)
            ).fetchone()
            emp = conn.execute(
                "SELECT EMP_ID FROM USER_DEPT WHERE EMP_ID = ?", (body.emp_id,)
            ).fetchone()
            if not room or not emp:
                raise HTTPException(status_code=400, detail="Invalid room_id or emp_id")

            conn.execute(
                """INSERT INTO CHAT_HISTORY
                   (CHAT_ID, ROOM_ID, EMP_ID, MESSAGE, USED_YN, COMPLIANCE_YN, CREATED_AT, CREATED_TM)
                   VALUES (?, ?, ?, ?, 1, ?, ?, ?)""",
                (chat_id, body.room_id, body.emp_id, masked, compliance_yn, today, created_tm),
            )
            return ChatMessageResponse(
                chat_id=chat_id,
                room_id=body.room_id,
                emp_id=body.emp_id,
                message=masked,
                used_yn=1,
                compliance_yn=compliance_yn,
                created_at=today,
                created_tm=created_tm,
            )

    result = await asyncio.to_thread(_insert)

    if is_closing_message(body.message):
        from app.scheduler import trigger_session_analysis

        asyncio.create_task(trigger_session_analysis(body.room_id))

    return result
