import { useCallback, useEffect, useState } from "react";
import AIRecommendModal from "./components/AIRecommendModal";
import MainChat from "./components/MainChat";
import {
  DEFAULT_ROOM_ID,
  EMP_ME,
  EMP_PARTNER,
  adoptRecommendation,
  fetchHistory,
  prepareRecommendations,
  sendMessage,
} from "./api/client";
import type { HistoryMessage, Recommendation, SpeakerMode } from "./types";

export default function App() {
  const [messages, setMessages] = useState<HistoryMessage[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [speakerMode, setSpeakerMode] = useState<SpeakerMode>("partner");
  const [inputValue, setInputValue] = useState("");
  const [statusText, setStatusText] = useState(
    "상대방 장애 문의 말풍선을 선택한 후 ✨ 버튼으로 AI 추천을 실행하세요.",
  );
  const [statusColor, setStatusColor] = useState("#64748B");
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchHistory(DEFAULT_ROOM_ID);
      setMessages(data);
    } catch {
      setStatusText("백엔드 연결 실패 — docker-compose up 후 새로고침하세요.");
      setStatusColor("#DC2626");
    }
  }, []);

  useEffect(() => {
    void loadHistory();
  }, [loadHistory]);

  const handleSelectMessage = (chatId: string) => {
    setSelectedChatId(chatId);
    setStatusText("선택된 장애 문의 맥락 분석 완료: AI 추천 검색 준비가 완료되었습니다.");
    setStatusColor("#4F46E5");
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text) return;
    const empId = speakerMode === "me" ? EMP_ME : EMP_PARTNER;
    try {
      await sendMessage(DEFAULT_ROOM_ID, empId, text);
      setInputValue("");
      await loadHistory();
    } catch {
      alert("메시지 전송 실패");
    }
  };

  const handleOpenAI = async () => {
    if (!selectedChatId) {
      alert("상대방의 장애 문의 말풍선을 먼저 선택해 주십시오.");
      return;
    }
    setModalOpen(true);
    setModalLoading(true);
    try {
      const result = await prepareRecommendations(
        selectedChatId,
        DEFAULT_ROOM_ID,
        EMP_ME,
      );
      setRecommendations(result.recommendations);
    } catch {
      alert("AI 추천 조회 실패");
      setModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const handleApply = async (text: string, rec: Recommendation) => {
    setInputValue(text);
    setModalOpen(false);
    if (selectedChatId) {
      try {
        await adoptRecommendation({
          chat_id: selectedChatId,
          room_id: DEFAULT_ROOM_ID,
          emp_id: EMP_ME,
          adopted_question: rec.adopted_question,
          adopted_answer: rec.adopted_answer,
          selected_type: rec.selected_type,
          keywords: rec.keywords,
          weight_score: rec.fused_score,
        });
      } catch {
        /* Qdrant may be unavailable in local dev — text injection still works */
      }
    }
    setStatusText("AI 추천 답변이 입력창에 반영되었습니다. 확인 후 전송하세요.");
    setStatusColor("#4F46E5");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <MainChat
        messages={messages}
        selectedChatId={selectedChatId}
        speakerMode={speakerMode}
        inputValue={inputValue}
        statusText={statusText}
        statusColor={statusColor}
        onSelectMessage={handleSelectMessage}
        onSpeakerChange={setSpeakerMode}
        onInputChange={setInputValue}
        onSend={() => void handleSend()}
        onOpenAI={() => void handleOpenAI()}
      />
      <AIRecommendModal
        open={modalOpen}
        loading={modalLoading}
        recommendations={recommendations}
        onClose={() => setModalOpen(false)}
        onApply={(text, rec) => void handleApply(text, rec)}
      />
    </div>
  );
}
