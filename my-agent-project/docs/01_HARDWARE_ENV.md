# INFRASTRUCTURE & HARDWARE CONSTRAINTS FOR AGENT

## 1. 시스템 하드웨어 스펙 (System Specifications)
* **CPU:** **AMD EPYC 7643 4-CORE PROCESSOR @ 2.30 GHZ (4 Cores / 4 Threads 제한)**
* **RAM:** **8GB DDR4 (극도의 제약 조건 - CRITICAL CONSTRAINT)**
* **DISK:** 100GB NVMe Storage

## 2. Agent용 셸 명령어 실행 및 제약 규칙 (CPU & RAM 동시 통제)
> ⚠️ **AI AGENT 필수 지시사항 (CRITICAL INSTRUCTION):**
> 현재 호스트 시스템은 CPU 4코어, RAM 8GB로 자원이 매우 타이트합니다. 셸(Shell)을 통해 빌드, 패키지 설치, 파이썬 배치를 기동할 때 병렬 프로세스 스레드 개수를 제한하지 않으면 CPU 100% 교착상태(Deadlock) 또는 RAM OOM(Out of Memory)이 발생합니다. 다음 실행 규칙을 반드시 엄수하십시오.

### [규칙 2.1] Docker 컨테이너 CPU 및 메모리 하드 한도 설정
`docker-compose.yml` 파일을 작성하거나 수정할 때, 컨테이너가 4코어 자원을 독점하지 않도록 CPU 주기(cpus)와 메모리(mem_limit)를 반드시 제약하십시오.
- **Frontend 컨테이너 (React):** `cpus: '0.5'`, `mem_limit: 1024m`
- **Backend 컨테이너 (FastAPI + SQLite):** `cpus: '1.0'`, `mem_limit: 1536m`
- **Vector DB 컨테이너 (Qdrant):** `cpus: '0.5'`, `mem_limit: 1024m`
- **LLM 컨테이너 (Ollama):** `cpus: '2.0'`, `mem_limit: 4096m` (Ollama 기동 시 CPU 코어 최대 2개까지만 할당 가능하도록 통제)

### [규칙 2.2] Node.js 힙 메모리 및 싱글 스레드 빌드 (Frontend Build)
셸에서 React 앱 빌드 시 싱글 워커로 안전하게 빌드되도록 강제하고, 힙 메모리를 제한하십시오.
```bash
NODE_OPTIONS="--max-old-space-size=1024" npm run build -- --max-workers=1