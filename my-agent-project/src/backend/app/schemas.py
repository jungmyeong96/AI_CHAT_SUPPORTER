"""Pydantic v2 request/response models aligned with contract.json."""

from typing import Literal

from pydantic import BaseModel, Field

SelectedType = Literal["OFFICIAL", "EXCELLENT", "GENERAL"]


class ChatMessageCreate(BaseModel):
    room_id: str
    emp_id: str
    message: str


class ChatMessageResponse(BaseModel):
    chat_id: str
    room_id: str
    emp_id: str
    message: str
    used_yn: int = 1
    compliance_yn: int
    created_at: str
    created_tm: str


class HistoryMessageItem(BaseModel):
    chat_id: str
    room_id: str
    emp_id: str
    emp_name: str
    dept_name: str
    message: str
    used_yn: int
    compliance_yn: int
    created_at: str | None
    created_tm: str


class ChatHistoryResponse(BaseModel):
    room_id: str
    total_count: int
    messages: list[HistoryMessageItem]


class RecommendPrepareRequest(BaseModel):
    chat_id: str
    room_id: str
    emp_id: str


class RecommendationItem(BaseModel):
    rank: int
    selected_type: SelectedType
    weight_multiplier: float
    cosine_score: float
    fused_score: float
    source_id: str
    adopted_question: str
    adopted_answer: str
    keywords: list[str]


class RecommendPrepareResponse(BaseModel):
    chat_id: str
    room_id: str
    emp_id: str
    dept_cd: str
    refined_keywords: list[str]
    recommendations: list[RecommendationItem]


class RecommendAdoptRequest(BaseModel):
    chat_id: str
    room_id: str
    emp_id: str
    adopted_question: str
    adopted_answer: str
    selected_type: SelectedType
    keywords: list[str]
    weight_score: float


class AdoptPayload(BaseModel):
    chat_id: str
    emp_id: str
    dept_cd: str
    adopted_question: str
    adopted_answer: str
    keywords: list[str]
    selected_type: SelectedType
    weight_score: float
    created_at: str
    created_tm: int


class RecommendAdoptResponse(BaseModel):
    adopt_id: str
    qdrant_upsert_status: Literal["success", "failed"]
    collection: str = "adopted_knowledge"
    vector_size: int
    payload: AdoptPayload
