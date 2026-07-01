from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class EventInput(BaseModel):
    minute: int
    second: Optional[int] = 0
    type: str
    team: Optional[str] = None
    player: Optional[str] = None
    outcome: Optional[str] = None
    extra: Optional[dict] = None


class MatchLoad(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    date: Optional[str] = None
    competition: Optional[str] = None
    events: Optional[List[EventInput]] = None


class MatchResponse(BaseModel):
    id: int
    match_id: str
    home_team: str
    away_team: str
    status: str

    class Config:
        from_attributes = True


class TurningPoint(BaseModel):
    minute: int
    momentum_delta: float
    direction: str  # "home" | "away"
    confidence: float


class CauseRanking(BaseModel):
    cause: str
    score: float
    evidence: List[str]


class AnalysisResponse(BaseModel):
    match_id: str
    turning_points: List[TurningPoint]
    cause_rankings: List[List[CauseRanking]]


class ExplanationResponse(BaseModel):
    match_id: str
    turning_point_index: int
    minute: int
    explanation: str
    causes: List[CauseRanking]


class ChatMessage(BaseModel):
    match_id: Optional[str] = None
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    reply: str
    context_used: Optional[str] = None
