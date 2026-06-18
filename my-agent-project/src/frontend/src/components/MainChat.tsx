import type { HistoryMessage, SpeakerMode } from "../types";

interface MainChatProps {
  messages: HistoryMessage[];
  selectedChatId: string | null;
  speakerMode: SpeakerMode;
  inputValue: string;
  statusText: string;
  statusColor: string;
  onSelectMessage: (chatId: string) => void;
  onSpeakerChange: (mode: SpeakerMode) => void;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onOpenAI: () => void;
}

export default function MainChat({
  messages,
  selectedChatId,
  speakerMode,
  inputValue,
  statusText,
  statusColor,
  onSelectMessage,
  onSpeakerChange,
  onInputChange,
  onSend,
  onOpenAI,
}: MainChatProps) {
  const partnerMessages = messages.filter((m) => m.emp_id !== "EMP1003");

  return (
    <div
      id="main-container"
      className="w-[760px] h-[857px] relative bg-[#D1D1D6] overflow-hidden select-none"
    >
      {/* Header */}
      <div
        id="chat-header-bar"
        className="w-[760px] h-[64px] absolute left-0 top-0 bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] border-b border-[#E2E8F0] z-10"
      >
        <div className="w-[40px] h-[40px] absolute left-[24px] top-[11.50px] bg-[#E2E8F0] rounded-full overflow-hidden border border-[#CBD5E1]" />
        <div className="absolute left-[76px] top-[9.50px] text-[13.20px] font-bold text-[#1E293B] font-inter">
          박SM
        </div>
        <div className="absolute left-[147.73px] top-[10px] w-[55.22px] h-[19px] bg-[#F1F5F9] rounded-[4px] flex items-center justify-center text-[9.4px] font-semibold text-[#475569]">
          여신운영
        </div>
        <div className="absolute left-[76px] top-[36.50px] text-[10.30px] text-[#94A3B8] font-normal font-inter">
          SM 개발자 · 장애 대응 R&R
        </div>

        <div className="absolute left-[462.45px] top-[12.50px] w-[211.55px] h-[38px] bg-[#F1F5F9] rounded-[12px] border border-[#E2E8F0]">
          <button
            type="button"
            onClick={() => onSpeakerChange("partner")}
            className={`absolute left-[5px] top-[5px] w-[93.39px] h-[28px] rounded-[8px] flex items-center justify-center text-[11.40px] font-bold transition-all ${
              speakerMode === "partner"
                ? "bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] text-[#1E293B]"
                : "text-[#64748B] bg-transparent"
            }`}
          >
            상대방
          </button>
          <button
            type="button"
            onClick={() => onSpeakerChange("me")}
            className={`absolute left-[118.39px] top-[5px] w-[93.39px] h-[28px] rounded-[8px] flex items-center justify-center text-[11.40px] font-bold transition-all ${
              speakerMode === "me"
                ? "bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)] text-[#1E293B]"
                : "text-[#64748B] bg-transparent top-[12px] bg-transparent shadow-none"
            }`}
          >
            나(SM)
          </button>
        </div>
      </div>

      {/* Chat stream */}
      <div
        id="chat-stream-zone"
        className="w-[760px] h-[660px] absolute left-0 top-[58px] overflow-y-auto overflow-x-hidden pb-4"
      >
        <div className="absolute left-[115.16px] top-[24px] w-[529.67px] h-[34.50px] bg-[#EEF2FF] rounded-full border border-[#E0E7FF] flex items-center px-4">
          <span className="text-[10.30px] text-[#4338CA]">
            🔒 금융 컴플라이언스 가드 활성 — 주민번호·계좌번호 자동 마스킹 적용
          </span>
        </div>

        <div className="relative mt-[70px] px-[24px] space-y-4">
          {partnerMessages.map((msg) => {
            const isSelected = selectedChatId === msg.chat_id;
            const isMe = msg.emp_id === "EMP1003";
            return (
              <div
                key={msg.chat_id}
                id={isSelected ? "msg-partner-question" : undefined}
                className={`max-w-[582px] cursor-pointer group ${isMe ? "ml-auto" : ""}`}
                onClick={() => onSelectMessage(msg.chat_id)}
              >
                <div className="text-[9px] text-[#94A3B8] mb-1">
                  {msg.emp_name} · {msg.dept_name}
                  {msg.compliance_yn === 1 && (
                    <span className="ml-2 text-[#4338CA] font-semibold">⚠ 컴플라이언스</span>
                  )}
                </div>
                <div
                  id={isSelected ? "msg-partner-bubble-2" : undefined}
                  className={`max-w-[420px] p-3 shadow-[0_2px_4px_rgba(0,0,0,0.1)] border transition-all duration-200 ${
                    isMe
                      ? "bg-[#EEF2FF] border-[#E0E7FF] rounded-tl-[16px] rounded-tr-[2px] rounded-br-[16px] rounded-bl-[16px] ml-auto"
                      : "bg-white rounded-tr-[16px] rounded-br-[16px] rounded-bl-[16px] rounded-tl-[2px] group-hover:border-[#4F46E5]"
                  } ${
                    isSelected
                      ? "border-[#4F46E5] bg-[#F5F3FF]"
                      : "border-transparent"
                  }`}
                >
                  <p
                    id={isSelected ? "msg-partner-content-2" : undefined}
                    className="text-[11.10px] text-[#1E293B] leading-[19.50px]"
                  >
                    {msg.message}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Input area */}
      <div
        id="chat-input-area"
        className="w-[760px] h-[133px] absolute left-0 top-[701px] bg-white border-t border-[#E2E8F0]"
      >
        <div className="px-[24px] pt-[12px]">
          <p
            id="mode-status-text"
            className="text-[10px] font-medium mb-2"
            style={{ color: statusColor }}
          >
            {statusText}
          </p>
          <div className="relative">
            <div className="w-[668px] h-[54px] bg-[#F8FAFC] rounded-[16px] border border-[#E2E8F0] relative flex items-center">
              <button
                id="btn-trigger-ai-recommend"
                type="button"
                onClick={onOpenAI}
                className="absolute left-[9px] top-[9px] w-[36px] h-[36px] bg-gradient-to-tr from-[#4F46E5] to-[#8B5CF6] rounded-[12px] flex items-center justify-center cursor-pointer shadow-md text-white text-sm"
                aria-label="AI 추천"
              >
                ✨
              </button>
              <input
                id="input-chat-message"
                type="text"
                value={inputValue}
                onChange={(e) => onInputChange(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onSend()}
                placeholder="메시지를 입력하세요..."
                className="flex-1 ml-[52px] mr-[80px] bg-transparent outline-none text-[12px] text-[#1E293B]"
              />
              <button
                type="button"
                onClick={onSend}
                className="absolute right-[12px] top-[11px] px-4 h-[32px] bg-[#4F46E5] text-white text-[11px] font-bold rounded-[8px]"
              >
                전송
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
