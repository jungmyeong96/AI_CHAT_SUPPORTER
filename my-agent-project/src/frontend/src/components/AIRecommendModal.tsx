import type { Recommendation } from "../types";
import { buildInjectText } from "../api/client";

interface AIRecommendModalProps {
  open: boolean;
  loading: boolean;
  recommendations: Recommendation[];
  onClose: () => void;
  onApply: (text: string, rec: Recommendation) => void;
}

const CARD_CONFIG = [
  {
    type: "OFFICIAL" as const,
    top: "88px",
    bg: "bg-[#EEF2FF]",
    border: "border-[#E0E7FF]",
    tagBg: "bg-[#DBCFFF]",
    tagText: "text-[#4338CA]",
    tagLabel: "📌 공식 준법 가이드 [1.50배]",
    btnBg: "bg-[#4F46E5]",
    id: "recommend-card-compliance",
    btnId: "btn-apply-compliance",
  },
  {
    type: "EXCELLENT" as const,
    top: "214px",
    bg: "bg-[#F5F3FF]",
    border: "border-[#EDE9FE]",
    tagBg: "bg-[#DDD6FE]",
    tagText: "text-[#6D28D9]",
    tagLabel: "👍 우수 채택 이력 [1.30배]",
    btnBg: "bg-[#7C3AED]",
    id: "recommend-card-history-best",
    btnId: "btn-apply-history-best",
  },
  {
    type: "GENERAL" as const,
    top: "340px",
    bg: "bg-[#F8FAFC]",
    border: "border-[#E2E8F0]",
    tagBg: "bg-[#E2E8F0]",
    tagText: "text-[#475569]",
    tagLabel: "💬 일반 업무 이력 [1.00배]",
    btnBg: "bg-[#64748B]",
    id: "recommend-card-history-general",
    btnId: "btn-apply-history-general",
  },
];

export default function AIRecommendModal({
  open,
  loading,
  recommendations,
  onClose,
  onApply,
}: AIRecommendModalProps) {
  if (!open) return null;

  const findRec = (type: string) =>
    recommendations.find((r) => r.selected_type === type);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div
        id="modal-recommend-container"
        className="w-[580px] h-[532px] relative bg-white rounded-[24px] shadow-[0px_10px_10px_-5px_rgba(0,0,0,0.04),0px_20px_25px_-5px_rgba(0,0,0,0.15)] border border-[#E2E8F0] overflow-hidden"
      >
        <button
          id="btn-close-modal"
          type="button"
          onClick={onClose}
          className="absolute left-[538.14px] top-[26.50px] w-[14.08px] text-[18px] text-[#94A3B8] cursor-pointer hover:text-slate-600 bg-transparent border-0"
          aria-label="닫기"
        >
          ×
        </button>

        <div
          id="modal-title"
          className="absolute left-[25px] top-[25px] text-[16px] font-bold text-[#1E293B] flex items-center"
        >
          ✨ AI 지능형 추천 답변
        </div>
        <div
          id="modal-subtitle-status"
          className="absolute left-[25px] top-[49px] text-[10.50px] font-medium text-[#64748B]"
        >
          {loading
            ? "맥락 분석 중..."
            : "최근 질문 맥락 분석 중 [고객 식별정보 마스킹 필터]가 실행되었습니다."}
        </div>

        {CARD_CONFIG.map((cfg) => {
          const rec = findRec(cfg.type);
          return (
            <div
              key={cfg.type}
              id={cfg.id}
              className={`absolute left-[25px] w-[532px] h-[112px] ${cfg.bg} rounded-[12px] border ${cfg.border}`}
              style={{ top: cfg.top }}
            >
              <div className="p-3 pr-[110px]">
                <div
                  className={`inline-flex w-auto h-[18px] px-2 ${cfg.tagBg} rounded-[4px] text-[8.50px] font-bold ${cfg.tagText} items-center justify-center mb-1`}
                >
                  {cfg.tagLabel}
                </div>
                <div className="text-[11.50px] font-bold text-[#1E293B] truncate">
                  {rec?.adopted_question ?? "—"}
                </div>
                <div className="text-[10px] text-[#475569] leading-[14.50px] line-clamp-2 mt-1">
                  {rec?.adopted_answer ?? "추천 데이터를 불러오는 중..."}
                </div>
              </div>
              <button
                id={cfg.btnId}
                type="button"
                disabled={!rec || loading}
                onClick={() => rec && onApply(buildInjectText(rec), rec)}
                className={`absolute left-[424px] top-[43px] w-[94px] h-[28px] ${cfg.btnBg} rounded-[6px] text-[10px] font-bold text-white flex items-center justify-center cursor-pointer shadow-xs disabled:opacity-50`}
              >
                채팅창 반영
              </button>
            </div>
          );
        })}

        <div
          id="modal-footer-tip"
          className="absolute left-[25px] top-[492px] text-[9.50px] font-bold text-[#94A3B8]"
        >
          💡 [채팅창 반영] 버튼을 클릭하면, 검증 완료된 텍스트 템플릿이 자동으로 입력창에
          마스킹된 상태로 삽입됩니다.
        </div>
      </div>
    </div>
  );
}
