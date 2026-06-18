"""SQLite context manager with WAL tuning."""

import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

DB_DIR = Path(os.getenv("DB_DIR", Path(__file__).resolve().parent.parent / "backend_data"))
DB_PATH = Path(os.getenv("DATABASE_PATH", DB_DIR / "ai_assistant.db"))
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"

DEFAULT_ROOM_ID = "ROOM-001"


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        _apply_pragmas(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    with get_connection() as conn:
        ddl = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(ddl)


def seed_demo_data() -> None:
    today = date.today().isoformat()
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM USER_DEPT").fetchone()[0]
        if count > 0:
            return

        conn.executemany(
            "INSERT INTO USER_DEPT (EMP_ID, EMP_NAME, DEPT_CD, DEPT_NAME, CREATED_AT) VALUES (?, ?, ?, ?, ?)",
            [
                ("EMP1001", "김운영", "DEPT001", "여신운영팀", today),
                ("EMP1002", "이준법", "DEPT002", "준법감시실", today),
                ("EMP1003", "박SM", "DEPT001", "여신운영팀", today),
            ],
        )
        conn.execute(
            "INSERT INTO CHAT_ROOM (ROOM_ID, ROOM_NAME, ROOM_TYPE, CREATED_AT) VALUES (?, ?, ?, ?)",
            (DEFAULT_ROOM_ID, "여신운영팀 소통방", "DEPARTMENT", today),
        )
        conn.executemany(
            "INSERT INTO CHAT_ROOM_MEMBER (ROOM_ID, EMP_ID) VALUES (?, ?)",
            [(DEFAULT_ROOM_ID, "EMP1001"), (DEFAULT_ROOM_ID, "EMP1002"), (DEFAULT_ROOM_ID, "EMP1003")],
        )
        conn.executemany(
            """INSERT INTO CHAT_HISTORY
               (CHAT_ID, ROOM_ID, EMP_ID, MESSAGE, USED_YN, COMPLIANCE_YN, CREATED_AT)
               VALUES (?, ?, ?, ?, 1, ?, ?)""",
            [
                (
                    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    DEFAULT_ROOM_ID,
                    "EMP1002",
                    "대리님, 이번 달 월마감 배치 업체 중에 이제나두 복지사 X123456789 고객의 매출 누락 건 확인 부탁드립니다.",
                    0,
                    today,
                ),
                (
                    "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                    DEFAULT_ROOM_ID,
                    "EMP1003",
                    "확인해보겠습니다..",
                    0,
                    today,
                ),
            ],
        )


def get_db() -> Generator[sqlite3.Connection, None, None]:
    with get_connection() as conn:
        yield conn
