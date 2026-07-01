from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Match, TurningPoint as TurningPointModel
from app.models.schemas import ChatMessage, ChatResponse, TurningPoint, CauseRanking
from app.modules import context_retrieval, granite_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatMessage, db: Session = Depends(get_db)):
    match_context = ""

    if payload.match_id:
        match = db.query(Match).filter(Match.match_id == payload.match_id).first()
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        tps = (
            db.query(TurningPointModel)
            .filter(TurningPointModel.match_id == match.id)
            .order_by(TurningPointModel.minute)
            .all()
        )
        if tps:
            # Use the highest-confidence turning point as primary context
            best_tp = max(tps, key=lambda t: t.confidence)
            tp = TurningPoint(
                minute=best_tp.minute,
                momentum_delta=best_tp.momentum_delta,
                direction=best_tp.direction,
                confidence=best_tp.confidence,
            )
            causes = [CauseRanking(**c) for c in (best_tp.causes or [])]
            match_context = context_retrieval.build_context(tp, causes, match.home_team, match.away_team)

    try:
        reply = granite_service.chat(payload.message, match_context, payload.history or [])
    except granite_service.GraniteUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return ChatResponse(reply=reply, context_used=match_context or None)
