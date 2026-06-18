"""APScheduler single-thread batch worker (F5) + closing event hook (F6)."""

import asyncio
import logging
import time
import uuid
from datetime import date, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.ollama_client import generate_keywords, get_embedding
from app.core.qdrant_engine import upsert_knowledge
from app.database import get_connection

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _scan_unrefined_sessions() -> None:
    """Scan CHAT_HISTORY for completed room sessions and upsert to Qdrant."""
    cutoff = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            rooms = conn.execute(
                """SELECT DISTINCT ROOM_ID FROM CHAT_HISTORY
                   WHERE USED_YN = 1 AND CREATED_TM <= ?""",
                (cutoff,),
            ).fetchall()

            for room in rooms:
                room_id = room["ROOM_ID"]
                messages = conn.execute(
                    """SELECT h.CHAT_ID, h.MESSAGE, h.EMP_ID, u.DEPT_CD
                       FROM CHAT_HISTORY h
                       JOIN USER_DEPT u ON h.EMP_ID = u.EMP_ID
                       WHERE h.ROOM_ID = ? AND h.USED_YN = 1
                       ORDER BY h.CREATED_TM ASC LIMIT 10""",
                    (room_id,),
                ).fetchall()
                if len(messages) < 2:
                    continue

                question = messages[0]["MESSAGE"]
                answer = messages[-1]["MESSAGE"]
                dept_cd = messages[0]["DEPT_CD"] or ""
                emp_id = messages[-1]["EMP_ID"]
                chat_id = messages[0]["CHAT_ID"]

                asyncio.run(_batch_upsert(chat_id, emp_id, dept_cd, question, answer))
    except Exception as exc:
        logger.warning("Batch scan failed: %s", exc)


async def _batch_upsert(
    chat_id: str, emp_id: str, dept_cd: str, question: str, answer: str
) -> None:
    keywords = await generate_keywords(f"{question} {answer}")
    vector = await get_embedding(f"{question} {answer}")
    adopt_id = str(uuid.uuid4())
    today = date.today().isoformat()
    payload = {
        "chat_id": chat_id,
        "emp_id": emp_id,
        "dept_cd": dept_cd,
        "adopted_question": question,
        "adopted_answer": answer,
        "keywords": keywords,
        "selected_type": "GENERAL",
        "weight_score": 1.0,
        "created_at": today,
        "created_tm": int(time.time()),
    }
    await upsert_knowledge(adopt_id, vector, payload)


async def trigger_session_analysis(room_id: str) -> None:
    """F6: Real-time hook on closing keyword detection."""
    try:
        with get_connection() as conn:
            messages = conn.execute(
                """SELECT h.CHAT_ID, h.MESSAGE, h.EMP_ID, u.DEPT_CD
                   FROM CHAT_HISTORY h
                   JOIN USER_DEPT u ON h.EMP_ID = u.EMP_ID
                   WHERE h.ROOM_ID = ? AND h.USED_YN = 1
                   ORDER BY h.CREATED_TM DESC LIMIT 5""",
                (room_id,),
            ).fetchall()
        if len(messages) < 2:
            return
        messages = list(reversed(messages))
        question = messages[0]["MESSAGE"]
        answer = messages[-1]["MESSAGE"]
        await _batch_upsert(
            messages[0]["CHAT_ID"],
            messages[-1]["EMP_ID"],
            messages[0]["DEPT_CD"] or "",
            question,
            answer,
        )
    except Exception as exc:
        logger.warning("Session analysis hook failed: %s", exc)


def start_scheduler() -> None:
    global _scheduler
    _scheduler = BackgroundScheduler(max_instances=1)
    _scheduler.add_job(
        _scan_unrefined_sessions,
        "interval",
        minutes=1,
        id="chat_session_scan",
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    logger.info("APScheduler started (1-minute interval, single thread)")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
