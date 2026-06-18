# DATA STORAGE SPECIFICATION (SQLITE & QDRANT)

## 1. 관계형 데이터베이스 스펙 (SQLite Embedded)
> ⚠️ **DBA & CODEGEN AGENT 필수 준수 사항:**
> - 본 프로젝트의 메인 RDB는 FastAPI 프로세스 내부 임베디드 모드로 작동하는 SQLite (`ai_assistant.db`)를 채택합니다.
> - `ADOPTED_HISTORY` 테이블은 데이터 중복 및 오버헤드를 막기 위해 RDB에서는 제외하고 **Qdrant Vector DB 단독 스토리지**로 완전 이관합니다.
> - SQLite 커넥션 직후 반드시 `PRAGMA journal_mode=WAL;` 및 `PRAGMA synchronous=NORMAL;` 튜닝 설정을 실행하도록 코드를 자동 빌드하십시오.

### [1.1] CHAT_HISTORY (원천 채팅 로그 테이블)
* **용도:** 실시간 대화 보존 및 금융 컴플라이언스(마스킹) 여부 시각화용 원천 데이터셋

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `CHAT_ID` | VARCHAR(50) | PRIMARY KEY | 대화 고유 식별자 (UUID v4 추천) |
| `ROOM_ID` | VARCHAR(50) | NOT NULL | CHAT_ROOM 참조 외래 키 역할 |
| `EMP_ID` | VARCHAR(20) | NOT NULL | USER_DEPT 참조 외래 키 역할 |
| `MESSAGE` | TEXT | NOT NULL | 원천 메시지 본문 (보안 필터 작동 시 마스킹 텍스트 적재) |
| `USED_YN` | TINYINT | DEFAULT 1 | 논리적 삭제 여부 (1: 사용, 0: 삭제) |
| `COMPLIANCE_YN` | TINYINT | DEFAULT 0 | 개인정보/계좌 등 위반 감지 여부 (1: 위반, 0: 정상) |
| `CREATED_AT` | VARCHAR(50) | NULL | YYYY-MM-DD 형태의 날짜 스트링 |
| `CREATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 일시 타임스탬프 |
| `UPDATED_AT` | VARCHAR(50) | NULL | 수정 날짜 스트링 |
| `UPDATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 최종 수정 타임스탬프 |

### [1.2] USER_DEPT (사원 및 부서 정보 테이블)
* **용도:** 금융 SM 권한 통제 및 Qdrant 컨텍스트 페이로드 필터링 매핑용 기준 테이블

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `EMP_ID` | VARCHAR(20) | PRIMARY KEY | 사원 번호 |
| `EMP_NAME` | VARCHAR(50) | NOT NULL | 사원명 |
| `DEPT_CD` | VARCHAR(50) | NULL | 부서 코드 (예: DEPT001) |
| `DEPT_NAME` | VARCHAR(100) | NOT NULL | 부서명 (예: 여신운영팀, 지불결제팀) |
| `CREATED_AT` | VARCHAR(50) | NULL | 최초 등록일 |
| `CREATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 타임스탬프 |
| `UPDATED_AT` | VARCHAR(50) | NULL | 수정일 |
| `UPDATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 최종 수정 타임스탬프 |

### [1.3] CHAT_ROOM (대화방 마스터 테이블)

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `ROOM_ID` | VARCHAR(50) | PRIMARY KEY | 대화방 고유 ID |
| `ROOM_NAME` | VARCHAR(150) | NOT NULL | 대화방 명칭 (예: 여신운영팀 소통방) |
| `ROOM_TYPE` | VARCHAR(20) | DEFAULT 'PERSONAL' | 방 유형 (PERSONAL / DEPARTMENT) |
| `CREATED_AT` | VARCHAR(50) | NULL | 생성일 |
| `CREATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 타임스탬프 |
| `UPDATED_AT` | VARCHAR(50) | NULL | 수정일 |
| `UPDATED_TM` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 최종 수정 타임스탬프 |

### [1.4] CHAT_ROOM_MEMBER (대화방 참여 사원 매핑 테이블)
* **복합키 제약:** `ROOM_ID`와 `EMP_ID`를 묶어 Composite Primary Key 지정.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `ROOM_ID` | VARCHAR(50) | PK, FK | CHAT_ROOM(ROOM_ID) 참조 |
| `EMP_ID` | VARCHAR(20) | PK, FK | USER_DEPT(EMP_ID) 참조 |
| `JOINED_AT` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 방 참여 시간 |

---

## 2. 벡터 데이터베이스 스펙 (Qdrant Vector DB Blueprint)
> ⚠️ **VECTOR DESIGN RULE FOR AGENT:**
> - 고 가치 정제 대화쌍 데이터인 `ADOPTED_HISTORY` 컬렉션은 CPU/RAM 부하 경감을 위해 온디스크(On-disk) 인덱스 및 정밀 페이로드 매칭 구조를 적용합니다.
> - 벡터 생성 모델: Ollama 로컬 임베딩 모델 표준 규격 준수 (기본 4096차원 또는 사용하는 임베딩 모델 차원에 동적 매핑, 코사인 유사도 채택)

### [2.1] Collection 명칭: `adopted_knowledge`

### [2.2] Vector Configuration (임베딩 설정)
- **Vector Size:** `4096` (또는 로컬 Ollama Embedding의 실제 Output 차원에 연동)
- **Distance Metric:** `Cosine` (유사도 측정 표준 알고리즘)
- **Index Option:** 8GB RAM 제약 조건으로 인해 메모리 적재를 최소화하도록 Payload 인덱스에 `keyword` 및 `text` 전용 On-disk 인덱싱 활성화 설정 부여.

### [2.3] Payload 데이터 세부 구조 (Qdrant JSON 스펙 정의)
CodeGen Agent가 Qdrant로 데이터를 `upsert`하거나 `search` 시 가중치 및 페이로드 필터 연산을 처리할 JSON 규격입니다.

```json
{
  "id": "UUID-v4-String (ADOPT_ID 매핑)",
  "vector": [0.0123, -0.4567, 0.8912, "... (총 4096 차원 실수 배열)"],
  "payload": {
    "chat_id": "string (원천 대화 CHAT_ID 매핑)",
    "emp_id": "string (최종 답변을 승인/등록한 사원번호)",
    "dept_cd": "string (소속 부서 코드 - 정밀 필터링 키)",
    "adopted_question": "text (현업 운영자가 질문한 실제 비정형 텍스트)",
    "adopted_answer": "text (준법 지침, 우수 답변 양식 또는 요약 정제된 최종 가이드라인)",
    "keywords": ["string", "string", "... (자카드 유사도 및 매칭 가속용 핵심 키워드 배열)"],
    "selected_type": "string (OFFICIAL: 준법감시실 지침 / EXCELLENT: 우수 업무 답변 / GENERAL: 일반 배치 이력)",
    "weight_score": 0.00, 
    "created_at": "string (YYYY-MM-DD)",
    "created_tm": 1781710520
  }
}