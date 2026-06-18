# 🏛️ Component Specification: Main Chat Interface (`main.html`)

본 문서는 가로 760px × 세로 857px 고정 해상도를 가진 금융 컴팩트 위젯의 메인 채팅 인터페이스 개발을 위한 정밀 명세서입니다. Cursor.ai 또는 CodeGen 에이전트는 본 명세와 구현 가이드라인을 1:1로 준수하여 개발해야 합니다.

## 1. 프로젝트 스크린 가이드라인 (Screen Overview)
- **해상도 규격:** `width: 760px`, `height: 857px` 고정 (유동적 반응형 금지).
- **레이아웃 방어:** 최외곽 Wrapper 컨테이너에 `overflow: hidden`, `position: relative`, `select-none` 사양을 선언하여 UI 픽셀 밀림이나 레이아웃 깨짐을 방지합니다.
- **스타일 표준:** Tailwind CSS를 사용하며, 원본 픽셀 단위를 인라인 커스텀 단위(`w-[760px]`, `text-[11.10px]`)로 정밀 변환합니다.

## 2. 컴포넌트 계층 구조 및 Tailwind CSS 매핑 명세

### 2.1 최상위 컨테이너 (`#main-container`)
- **역할:** 전체 대화창 캔버스 베이스 역할 수행.
- **스타일:** `w-[760px] h-[857px] relative bg-[#D1D1D6] overflow-hidden`

### 2.2 상단 헤더 영역 (`#chat-header-bar`)
- **스타일:** `w-[760px] h-[64px] absolute left-0 top-0 bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] border-b border-[#E2E8F0]`
- **내부 하위 컴포넌트:**
  1. `header-avatar` (지정 프로필): `w-40px h-40px absolute left-[24px] top-[11.50px] bg-[#E2E8F0] rounded-full overflow-hidden border border-[#CBD5E1]`
  2. `header-user-name` (사용자명): `absolute left-[76px] top-[9.50px] text-[13.20px] font-bold text-[#1E293B] font-['Inter']`
  3. `header-user-dept-badge` (부서 배지): `absolute left-[147.73px] top-[10px] w-[55.22px] h-[19px] bg-[#F1F5F9] rounded-[4px] flex items-center justify-center text-[9.4px] font-semibold text-[#475569]`
  4. `header-user-rr` (R&R 설명문): `absolute left-[76px] top-[36.50px] text-[10.30px] text-[#94A3B8] font-normal font-['Inter']`
  5. `header-filter-switch` (발화 주체 토글 스위치): `absolute left-[462.45px] top-[12.50px] w-[211.55px] h-[38px] bg-[#F1F5F9] rounded-[12px] border border-[#E2E8F0]`
     - `tab-filter-partner` (활성 탭 예시): `absolute left-[5px] top-[5px] w-[93.39px] h-[28px] bg-white rounded-[8px] shadow-[0_1px_2px_rgba(0,0,0,0.05)] flex items-center justify-center text-[11.40px] font-bold text-[#1E293B]`
     - `tab-filter-me` (비활성 탭 예시): `absolute left-[118.39px] top-[12px] text-[11.40px] font-bold text-[#64748B]`

### 2.3 채팅 스트림 뷰 (`#chat-stream-zone`)
- **스타일:** `w-[760px] h-[660px] absolute left-0 top-[58px] overflow-hidden`
- **내부 메시지 타임라인 구성:**
  1. `compliance-banner` (보안 공지): `absolute left-[115.16px] top-[24px] w-[529.67px] h-[34.50px] bg-[#EEF2FF] rounded-full border border-[#E0E7FF] flex items-center px-4`
     - 텍스트 컬러: `#4338CA`, 폰트 크기: `text-[10.30px]`, 자물쇠 기호 표기 포함.
  2. `msg-partner-question` (핵심 장애 문의 - 상대방): `absolute left-[24px] top-[132px] w-[582px] h-[105.50px] cursor-pointer group`
     - **인터랙션 타겟:** 마우스 클릭 시 Active Border 효과를 동적 부여합니다.
     - `msg-partner-bubble-2` (말풍선 본문): `w-[420px] bg-white rounded-tr-[16px] rounded-br-[16px] rounded-bl-[16px] rounded-tl-[2px] p-3 shadow-[0_2px_4px_rgba(0,0,0,0.1)] border border-transparent transition-all duration-200 group-hover:border-[#4F46E5]`
     - 내부 텍스트 (`#msg-partner-content-2`): `text-[11.10px] text-[#1E293B] leading-[19.50px]` ("대리님, 이번 달 월마감 배치 업체 중에... X123456789 고객의...")
  3. `msg-me-pending` (나/SM 개발자 응답): 배경 `#EEF2FF`, 테두리 `#E0E7FF`, 텍스트 "확인해보겠습니다.." 구현.

### 2.4 하단 입력 및 조작 제어 영역 (`#chat-input-area`)
- **스타일:** `w-[760px] h-[133px] absolute left-0 top-[701px] bg-white border-t border-[#E2E8F0]`
- **하위 컴포넌트:**
  1. `input-mode-container` (상태 제어 바): 답변/질문 모드 선택 스위치 스위칭. `mode-status-text` 영역에 프로세스 설명 가이드 동적 바인딩.
  2. `input-field-container` (메시지 인풋창 배경 박스): `w-[668px] h-[54px] bg-[#F8FAFC] rounded-[16px] border border-[#E2E8F0] relative`
  3. `input-chat-message` (리얼 텍스트 필드): `input[type="text"]`, `placeholder` 장착 및 외부 주입 텍스트 수신 대기.
  4. `btn-trigger-ai-recommend` (핵심 AI 모달 트리거 버튼 ✨): `absolute left-[9px] top-[9px] w-[36px] h-[36px] bg-gradient-to-tr from-[#4F46E5] to-[#8B5CF6] rounded-[12px] flex items-center justify-center cursor-pointer shadow-md`

## 3. 핵심 화면 흐름 및 상태 제어 자바스크립트 가이드

CodeGen 에이전트는 단일 SPA 구조 혹은 Vanilla JS 인터랙션 핸들러 구현 시 아래의 흐름을 보장해야 합니다.

```javascript
// 1. 말풍선 선택 (Selection) 이벤트 상태 바인딩
let currentSelectedChatId = null;

function bindMessageSelection() {
    const partnerMsg = document.getElementById('msg-partner-question');
    partnerMsg.addEventListener('click', () => {
        currentSelectedChatId = 'CHAT_002';
        
        // 시각화 이펙트 적용 (Active Border)
        const bubble = document.getElementById('msg-partner-bubble-2');
        bubble.style.borderColor = '#4F46E5';
        bubble.style.backgroundColor = '#F5F3FF';
        
        // 하단 가이드 텍스트 상태 변경 알림
        const statusText = document.getElementById('mode-status-text');
        statusText.innerText = "선택된 장애 문의 맥락 분석 완료: AI 추천 검색 준비가 완료되었습니다.";
        statusText.style.color = "#4F46E5";
    });
}

// 2. AI 추천 모달 가동 시퀀스 매핑
function bindAITrigger() {
    const aiBtn = document.getElementById('btn-trigger-ai-recommend');
    aiBtn.addEventListener('click', () => {
        if (!currentSelectedChatId) {
            alert("상대방의 장애 문의 말풍선을 먼저 선택해 주십시오.");
            return;
        }
        // 백엔드 RAG 비동기 조회 가상화 시뮬레이션 및 글로벌 이벤트 디스패치
        console.log("POST /api/v1/ai/recommend/prepare 발생");
        window.dispatchEvent(new CustomEvent('OPEN_AI_RECOMMEND_MODAL', { 
            detail: { chatId: currentSelectedChatId } 
        }));
    });
}