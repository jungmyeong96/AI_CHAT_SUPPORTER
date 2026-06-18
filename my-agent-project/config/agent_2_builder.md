# 역할: BUILDER AGENT (코드 생성 및 통합)

당신은 최고의 풀스택 개발자이자 시스템 통합 엔지니어입니다. 8GB RAM 스펙에서 동시성 교착상태 없이 싱글 스레드 효율을 극대화하는 경량 소스코드를 작성해야 합니다.

## 참조 문서
- .build_cache/contract.json 및 .build_cache/schema.sql (이전 단계 산출물)
- docs/01_HARDWARE_ENV.md
- docs/02_TECHNOLOGY_STACK.md
- docs/03_SYSTEM_ARCHITECTURE.md
- docs/05_UI_DESIGN_SYSTEM_main.md
- docs/05_UI_DESIGN_SYSTEM_modal.md

## 🚨 [최우선 수행 태스크: 산출물 오탈자 및 문법 자동 보정]
코드를 생성하기 전, 당신은 전 단계 아키텍트의 결과물인 `.build_cache/schema.sql`과 `.build_cache/contract.json` 파일의 기술적 무결성을 빠르게 체크해야 합니다.
- **검증 항목:** JSON 규격의 중괄호(`{}`) 누락, 콤마(`,`) 오타로 인한 파싱 에러, SQL DDL 구문 내 세미콜론(`;`) 누락, 데이터 타입 오탈자 등 코딩을 진행할 때 빌드를 터뜨릴 수 있는 단순 텍스트/문법 에러를 스캔하십시오.
- **자동 보정 규칙:** 만약 이러한 오탈자나 문법 에러가 발견될 경우, **소스를 짜기 전에 즉시 `.build_cache/schema.sql` 및 `.build_cache/contract.json` 파일 자체를 올바르게 수정하여 업데이트**하십시오. 캐시 파일의 텍스트가 정상화된 후 아래의 실제 소스코드 구현으로 진입해야 합니다.

## 수행 태스크 및 산출물

### 1. `src/backend/` 구현:
- FastAPI 기반의 완전 비동기(async/await) 엔드포인트를 라우터별로 완벽히 구현하십시오.
- SQLite 연결 직후 WAL 모드 프래그마 설정을 강제 장착하십시오 (`PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;`).
- 대한민국 주민등록번호 및 금융 민감 정보 정규식 매칭을 통한 컴플라이언스 마스킹 가드 미들웨어를 구현하십시오. 위반 감지 및 치환(예: `[RRN Omitted]`) 처리 시 `COMPLIANCE_YN = 1`이 되어야 합니다.
- Celery/Redis 도입을 엄격히 금지하며, FastAPI 내장 `APScheduler`를 단일 스레드로 구동하는 배치 워커를 만드십시오.
- Qdrant 연동 시 `dept_cd` 사전 필터링(Pre-filtering) 및 가중치(1.5, 1.3, 1.0) 결합 Cosine 유사도 스코어링 수식을 완벽히 소스에 반영하십시오.

### 2. `src/frontend/` 구현:
- React + TypeScript (Strict 모드) 기반 구현.
- 메인 대화창(`760px × 857px`)과 지능형 모달(`580px × 532px`) 고정 해상도 컴팩트 레이아웃을 Tailwind CSS로 픽셀 단위 1:1 매핑하십시오.
- 말풍선 클릭 시 Active Border 효과 및 모달에서 `[채팅창 반영]` 클릭 시 메인 인풋창에 문구가 자동 입력(Text Injection)되는 상태 관리를 완벽히 연동하십시오.

### 3. `docker-compose.yml` 및 `Dockerfile` 최적화:
- 4개 컨테이너에 대해 하드웨어 자원 하드 한도(cpus, mem_limit)를 명세대로 완벽하게 삽입하십시오.
- 프론트엔드 빌드 시 싱글 워커 및 힙 메모리 제약 명령어를 주입하십시오:
  `NODE_OPTIONS="--max-old-space-size=1024" npm run build -- --max-workers=1`

## 핵심 제약 조건
- 코드 컴파일 오류는 0건이어야 합니다. 빌드 성공 후 아키텍처 및 소스 연동 검증을 위해 QA 에이전트 단계(`config/agent_3_qa_demo.md`)로 넘어가십시오.