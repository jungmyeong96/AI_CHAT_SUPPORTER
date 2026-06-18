# ✨ Component Specification: AI Intelligent Recommendations Modal (`modal.html`)

본 문서는 대화 맥락, 사내 문서, 과거 장애 조치 이력을 RAG(Retrieval-Augmented Generation) 알고리즘으로 추출 및 가공하여 완벽한 해결책을 제안하는 오버레이 모달 컴포넌트 개발 지시서입니다. Cursor.ai 또는 CodeGen 에이전트는 본 명세와 가이드라인을 1:1로 준수하여 개발해야 합니다.

## 1. 프로젝트 스크린 가이드라인 (Screen Overview)
- **모달 컴포넌트 해상도 규격:** `width: 580px`, `height: 532px` 고정 프레임.
- **스타일 제어 규칙:** 배경 `bg-white`, 라운드 처리 `rounded-[24px]`, 외부 아웃라인 오프셋 배치 및 복합 드롭 섀도(`shadow-[0px_10px_10px_-5px_rgba(0,0,0,0.04),0px_20px_25px_-5px_rgba(0,0,0,0.15)]`) 사양을 정확히 강제합니다.
- **레이아웃 방어:** 컴팩트 위젯 크기 내에서 카드 데이터 리스트가 유실되지 않도록 내부에 독립 스크롤 영역을 두거나 고정 픽셀 배치를 철저하게 준수합니다.

## 2. 컴포넌트 계층 구조 및 Tailwind CSS 매핑 명세

### 2.1 최상위 레이어 컨테이너 (`#modal-recommend-container`)
- **스타일:** `w-[580px] h-[532px] relative bg-white rounded-[24px] shadow-2xl border border-[#E2E8F0] overflow-hidden`
- **`btn-close-modal`** (우측 상단 닫기 인터랙션): `absolute left-[538.14px] top-[26.50px] w-[14.08px] text-[18px] text-[#94A3B8] cursor-pointer hover:text-slate-600`

### 2.2 헤더 및 보안 인디케이터 영역
- **`modal-title`** (메인 헤드라인 타이틀): `absolute left-[25px] top-[25px] text-[16px] font-bold text-[#1E293B] flex items-center` 
  - 문구 내용: `✨ AI 지능형 추천 답변`
- **`modal-subtitle-status`** (엔진 마스킹 상태 정보): `absolute left-[25px] top-[49px] text-[10.50px] font-medium text-[#64748B]`
  - 문구 내용: `이여신 과장의 최근 질문 맥락 분석 중 [고객 식별정보 마스킹 필터]가 실행되었습니다.`

### 2.3 추천 결과 템플릿 리스트 카드 스트림 (수직 스택 구조 배치)

#### ① 추천 항목 1: 사내 규정 준법 가이드 (`#recommend-card-compliance`)
- **스타일:** `absolute left-[25px] top-[88px] w-[532px] h-[112px] bg-[#EEF2FF] rounded-[12px] border border-[#E0E7FF]`
- **`tag-compliance-weight`** (가중치 뱃지): `w-[155px] h-[18px] bg-[#DBCFFF] rounded-[4px] text-[8.50px] font-bold text-[#4338CA] flex items-center justify-center` 
  - 표기 텍스트: `📌 공식 준법 가이드 [1.50배]`
- **`title-compliance-card`** (타이틀): `text-[11.50px] font-bold text-[#1E293B]`
  - 표기 텍스트: `이제나두 복지사 마감 지연 수기조정 규정`
- **`content-compliance-card`** (본문): `text-[10px] text-[#475569] leading-[14.50px]`
  - 본문 내용: "월마감 배치 누락 시... '수기 마감 조정 메뉴(#402)'에서..."
- **`btn-apply-compliance`** (반영 액션 버튼): `absolute left-[424px] top-[43px] w-[94px] h-[28px] bg-[#4F46E5] rounded-[6px] text-[10px] font-bold text-white flex items-center justify-center cursor-pointer shadow-xs`

#### ② 추천 항목 2: 과거 우수 조치 이력 (`#recommend-card-history-best`)
- **스타일:** `absolute left-[25px] top-[214px] w-[532px] h-[112px] bg-[#F5F3FF] rounded-[12px] border border-[#EDE9FE]`
- **`tag-history-best-weight`** (뱃지): `bg-[#DDD6FE] text-[#6D28D9]` 
  - 표기 텍스트: `👍 우수 채택 이력 [1.30배]`
- **`title-history-best-card`** (타이틀): `가맹점 코드 싱크 및 매핑 테이블 동기화 이력`
- **`btn-apply-history-best`** (액션 버튼): `w-[94px] h-[28px] bg-[#7C3AED] rounded-[6px] text-white flex items-center justify-center text-[10px] font-bold cursor-pointer`

#### ③ 추천 항목 3: 일반 업무 히스토리 (`#recommend-card-history-general`)
- **스타일:** `absolute left-[25px] top-[340px] w-[532px] h-[112px] bg-[#F8FAFC] rounded-[12px] border border-[#E2E8F0]`
- **`tag-history-general-weight`** (뱃지): `bg-[#E2E8F0] text-[#475569]` 
  - 표기 텍스트: `💬 일반 업무 이력 [1.00배]`
- **`title-history-general-card`** (타이틀): `지연입금 복지정산 지불결제팀 R&R 담당자 확인`
- **`btn-apply-history-general`** (액션 버튼): `w-[94px] h-[28px] bg-[#64748B] rounded-[6px] text-white flex items-center justify-center text-[10px] font-bold cursor-pointer`

### 2.4 하단 푸터 팁 가이드
- **`modal-footer-tip`** (설명 구역): `absolute left-[25px] top-[492px] text-[9.50px] font-bold text-[#94A3B8]`
  - 문구 내용: `💡 [채팅창 반영] 버튼을 클릭하면, 검증 완료된 텍스트 템플릿이 자동으로 입력창에 마스킹된 상태로 삽입됩니다.`

## 3. 컴포넌트 간 데이터 인젝션(Injection) 공유 인터랙션 코드 가이드

각 추천 카드의 `[채팅창 반영]` 이벤트가 발생했을 때 부모 윈도우(`main.html`)의 채팅 입력 엘리먼트 값에 정밀 파싱 텍스트를 인젝션하는 상호운용성 스크립트 가이드입니다.

```javascript
// [채팅창 반영] 액션 이벤트 핸들러 바인딩 파이프라인
function setupModalActionHandlers() {
    // 1. 컴플라이언스 카드 채택 이벤트
    const btnApplyCompliance = document.getElementById('btn-apply-compliance');
    if(btnApplyCompliance) {
        btnApplyCompliance.addEventListener('click', () => {
            const textTemplate = "[공식 준법 가이드] 월마감 배치 누락 시, 당월 배치를 무리하게 재수행하지 않고 '수기 마감 조정 메뉴(#402)'에서 파트너 코드(이제나두) 강제 조정을 통해 정산 마감 처리를 진행하는 방향을 권고합니다.";
            injectTextToMainChatInput(textTemplate);
        });
    }

    // 2. 우수 히스토리 카드 채택 이벤트를 통한 가맹점 동기화 정보 주입
    const btnApplyHistoryBest = document.getElementById('btn-apply-history-best');
    if(btnApplyHistoryBest) {
        btnApplyHistoryBest.addEventListener('click', () => {
            const textTemplate = "[과거 우수 조치 이력 매칭] 이전 이제나두 복지사 매출 누락 건의 경우 가맹점 매핑 마스터 테이블(TB_PARTNER_MAP) 내 고객 마스킹 식별 정보가 누락된 원인이 확인되었으니 싱크 상태 확인을 바랍니다.";
            injectTextToMainChatInput(textTemplate);
        });
    }
}

// 부모 입력 필드로 최종 데이터를 전송하고 마이그레이션 싱크를 연동하는 공통 헬퍼 함수
function injectTextToMainChatInput(content) {
    // iframe 내 임베디드 구조이거나 단일 DOM 구조일 경우를 둘 다 방어 처리
    const mainChatInput = window.parent.document.getElementById('input-chat-message') || document.getElementById('input-chat-message');
    if (mainChatInput) {
        mainChatInput.value = content;
        mainChatInput.focus();
        
        // 데이터 전송 완료 후 로그 추적 출력
        console.log("Qdrant Vector Store 및 SQLite 확정 스키마 데이터 동기화 완료.");
        
        // 모달창 자동 닫기 디스패치 트리거 호출
        const closeBtn = document.getElementById('btn-close-modal');
        if(closeBtn) closeBtn.click();
    }
}