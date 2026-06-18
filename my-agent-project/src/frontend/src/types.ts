export type SelectedType = "OFFICIAL" | "EXCELLENT" | "GENERAL";

export interface HistoryMessage {
  chat_id: string;
  room_id: string;
  emp_id: string;
  emp_name: string;
  dept_name: string;
  message: string;
  used_yn: number;
  compliance_yn: number;
  created_at: string | null;
  created_tm: string;
}

export interface Recommendation {
  rank: number;
  selected_type: SelectedType;
  weight_multiplier: number;
  cosine_score: number;
  fused_score: number;
  source_id: string;
  adopted_question: string;
  adopted_answer: string;
  keywords: string[];
}

export interface PrepareResponse {
  chat_id: string;
  room_id: string;
  emp_id: string;
  dept_cd: string;
  refined_keywords: string[];
  recommendations: Recommendation[];
}

export type SpeakerMode = "partner" | "me";
