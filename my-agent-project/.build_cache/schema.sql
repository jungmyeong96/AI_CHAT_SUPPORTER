-- =============================================================================
-- AI Assistant Embedded SQLite Schema (ai_assistant.db)
-- Architect Agent Output | FastAPI In-Process Embedded Mode
-- =============================================================================
--
-- [CONNECTION PRAGMA - MUST EXECUTE IMMEDIATELY AFTER EACH CONNECTION OPEN]
--   PRAGMA journal_mode=WAL;      -- Write-Ahead Logging: concurrent read/write, lock timeout prevention
--   PRAGMA synchronous=NORMAL;    -- WAL mode safe default; fsync cost reduction under 8GB RAM constraint
--
-- [DESIGN NOTE]
--   ADOPTED_HISTORY is intentionally EXCLUDED from SQLite DDL.
--   High-value adopted Q&A pairs are stored exclusively in Qdrant collection `adopted_knowledge`
--   to prevent RDB/Vector data duplication and reduce embedded DB overhead.
--
-- [HARDWARE CONTEXT]
--   Host: AMD EPYC 4-Core / 8GB RAM | Backend container: cpus 1.0, mem_limit 1536m
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- [1.1] USER_DEPT - Employee & Department Master (referenced by other tables)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS USER_DEPT (
    EMP_ID      TEXT        NOT NULL,
    EMP_NAME    TEXT        NOT NULL,
    DEPT_CD     TEXT,
    DEPT_NAME   TEXT        NOT NULL,
    CREATED_AT  TEXT,
    CREATED_TM  TEXT        DEFAULT (datetime('now', 'localtime')),
    UPDATED_AT  TEXT,
    UPDATED_TM  TEXT        DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (EMP_ID)
);

CREATE INDEX IF NOT EXISTS idx_user_dept_dept_cd
    ON USER_DEPT (DEPT_CD);

-- -----------------------------------------------------------------------------
-- [1.2] CHAT_ROOM - Chat Room Master
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CHAT_ROOM (
    ROOM_ID     TEXT        NOT NULL,
    ROOM_NAME   TEXT        NOT NULL,
    ROOM_TYPE   TEXT        DEFAULT 'PERSONAL'
                            CHECK (ROOM_TYPE IN ('PERSONAL', 'DEPARTMENT')),
    CREATED_AT  TEXT,
    CREATED_TM  TEXT        DEFAULT (datetime('now', 'localtime')),
    UPDATED_AT  TEXT,
    UPDATED_TM  TEXT        DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (ROOM_ID)
);

CREATE INDEX IF NOT EXISTS idx_chat_room_type
    ON CHAT_ROOM (ROOM_TYPE);

-- -----------------------------------------------------------------------------
-- [1.3] CHAT_ROOM_MEMBER - Room Membership Mapping (Composite PK)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CHAT_ROOM_MEMBER (
    ROOM_ID     TEXT        NOT NULL,
    EMP_ID      TEXT        NOT NULL,
    JOINED_AT   TEXT        DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (ROOM_ID, EMP_ID),
    FOREIGN KEY (ROOM_ID) REFERENCES CHAT_ROOM (ROOM_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (EMP_ID)  REFERENCES USER_DEPT (EMP_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_room_member_emp
    ON CHAT_ROOM_MEMBER (EMP_ID);

-- -----------------------------------------------------------------------------
-- [1.4] CHAT_HISTORY - Source Chat Log (Compliance Masking Target)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CHAT_HISTORY (
    CHAT_ID         TEXT    NOT NULL,
    ROOM_ID         TEXT    NOT NULL,
    EMP_ID          TEXT    NOT NULL,
    MESSAGE         TEXT    NOT NULL,
    USED_YN         INTEGER DEFAULT 1
                            CHECK (USED_YN IN (0, 1)),
    COMPLIANCE_YN   INTEGER DEFAULT 0
                            CHECK (COMPLIANCE_YN IN (0, 1)),
    CREATED_AT      TEXT,
    CREATED_TM      TEXT    DEFAULT (datetime('now', 'localtime')),
    UPDATED_AT      TEXT,
    UPDATED_TM      TEXT    DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (CHAT_ID),
    FOREIGN KEY (ROOM_ID) REFERENCES CHAT_ROOM (ROOM_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (EMP_ID)  REFERENCES USER_DEPT (EMP_ID)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Performance indexes: room history lookup + ASC time ordering + active record filter
CREATE INDEX IF NOT EXISTS idx_chat_history_room_active
    ON CHAT_HISTORY (ROOM_ID, USED_YN, CREATED_TM ASC);

CREATE INDEX IF NOT EXISTS idx_chat_history_emp
    ON CHAT_HISTORY (EMP_ID);

CREATE INDEX IF NOT EXISTS idx_chat_history_compliance
    ON CHAT_HISTORY (ROOM_ID, COMPLIANCE_YN)
    WHERE USED_YN = 1;

-- -----------------------------------------------------------------------------
-- [QDRANT ONLY] adopted_knowledge collection payload reference (NOT in SQLite)
-- -----------------------------------------------------------------------------
-- Collection : adopted_knowledge
-- Vector Size: 4096 | Distance: Cosine | On-disk payload index enabled
-- Payload keys: chat_id, emp_id, dept_cd, adopted_question, adopted_answer,
--               keywords[], selected_type, weight_score, created_at, created_tm
