import axios from "axios";
import type { HistoryMessage, PrepareResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "",
  headers: { "Content-Type": "application/json" },
});

export const DEFAULT_ROOM_ID = "ROOM-001";
export const EMP_ME = "EMP1003";
export const EMP_PARTNER = "EMP1002";

export async function fetchHistory(roomId: string): Promise<HistoryMessage[]> {
  const { data } = await api.get<{ messages: HistoryMessage[] }>(
    `/api/v1/chat/rooms/${roomId}/history`,
  );
  return data.messages;
}

export async function sendMessage(
  roomId: string,
  empId: string,
  message: string,
): Promise<HistoryMessage> {
  const { data } = await api.post<HistoryMessage>("/api/v1/chat/message", {
    room_id: roomId,
    emp_id: empId,
    message,
  });
  return data;
}

export async function prepareRecommendations(
  chatId: string,
  roomId: string,
  empId: string,
): Promise<PrepareResponse> {
  const { data } = await api.post<PrepareResponse>("/api/v1/ai/recommend/prepare", {
    chat_id: chatId,
    room_id: roomId,
    emp_id: empId,
  });
  return data;
}

export async function adoptRecommendation(payload: {
  chat_id: string;
  room_id: string;
  emp_id: string;
  adopted_question: string;
  adopted_answer: string;
  selected_type: string;
  keywords: string[];
  weight_score: number;
}): Promise<void> {
  await api.post("/api/v1/ai/recommend/adopt", payload);
}

export function buildInjectText(rec: {
  selected_type: string;
  adopted_answer: string;
}): string {
  const prefixMap: Record<string, string> = {
    OFFICIAL: "[공식 준법 가이드]",
    EXCELLENT: "[과거 우수 조치 이력 매칭]",
    GENERAL: "[일반 업무 이력]",
  };
  const prefix = prefixMap[rec.selected_type] ?? "[AI 추천]";
  return `${prefix} ${rec.adopted_answer}`;
}
