import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Match, Event, TurningPoint as TurningPointModel, Explanation
from app.models.schemas import MatchLoad, MatchResponse, AnalysisResponse, ExplanationResponse
from app.modules import preprocessing, feature_extraction, momentum_detection, cause_ranking, context_retrieval, granite_service
from app.modules.ingestion import load_match_from_json, load_match_from_dict

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/load", response_model=MatchResponse)
def load_match(payload: MatchLoad, db: Session = Depends(get_db)):
    existing = db.query(Match).filter(Match.match_id == payload.match_id).first()
    if existing:
        return existing

    # If events are provided, use the full ingestion path
    if payload.events:
        data = {
            "match_id": payload.match_id,
            "home_team": payload.home_team,
            "away_team": payload.away_team,
            "date": payload.date,
            "competition": payload.competition,
            "events": [evt.model_dump() for evt in payload.events],
        }
        match = load_match_from_dict(data, db)
        return match

    # Fallback: create match record without events
    match = Match(
        match_id=payload.match_id,
        home_team=payload.home_team,
        away_team=payload.away_team,
        date=payload.date,
        competition=payload.competition,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.post("/load-file", response_model=MatchResponse)
async def load_match_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a match JSON file (like sample_match.json) to load a match with all its events."""
    try:
        content = await file.read()
        data = json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")

    if "match_id" not in data or "home_team" not in data or "away_team" not in data:
        raise HTTPException(status_code=422, detail="JSON must contain match_id, home_team, and away_team")

    match = load_match_from_dict(data, db)
    return match


@router.post("/{match_id}/analyze", response_model=AnalysisResponse)
def analyze_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    events_df = preprocessing.load_events_as_df(match.id, db)
    if events_df.empty:
        raise HTTPException(status_code=422, detail="No events found for this match")

    preprocessed = preprocessing.preprocess_events(events_df, match.home_team)
    features_df = feature_extraction.extract_features(preprocessed, match.id)
    feature_extraction.save_features(features_df, match.id, db)

    tps = momentum_detection.detect_turning_points(features_df)
    saved_tps = momentum_detection.save_turning_points(tps, match.id, db)

    all_causes = []
    for tp in tps:
        causes = cause_ranking.rank_causes(preprocessed, tp.minute)
        all_causes.append(causes)
        # Persist top causes on the turning point model
        db_tp = next((t for t in saved_tps if t.minute == tp.minute), None)
        if db_tp:
            db_tp.causes = [c.model_dump() for c in causes[:5]]
    db.commit()

    match.status = "analyzed"
    db.commit()

    return AnalysisResponse(match_id=match_id, turning_points=tps, cause_rankings=all_causes)


@router.post("/{match_id}/explain/{turn_index}", response_model=ExplanationResponse)
def explain_turning_point(match_id: str, turn_index: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    tps = db.query(TurningPointModel).filter(TurningPointModel.match_id == match.id).order_by(TurningPointModel.minute).all()
    if turn_index >= len(tps):
        raise HTTPException(status_code=404, detail="Turning point index out of range")

    tp_model = tps[turn_index]
    from app.models.schemas import TurningPoint, CauseRanking
    tp = TurningPoint(
        minute=tp_model.minute,
        momentum_delta=tp_model.momentum_delta,
        direction=tp_model.direction,
        confidence=tp_model.confidence,
    )
    causes = [CauseRanking(**c) for c in (tp_model.causes or [])]

    ctx = context_retrieval.build_context(tp, causes, match.home_team, match.away_team)

    try:
        explanation_text = granite_service.generate_explanation(ctx)
    except granite_service.GraniteUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))

    exp = Explanation(match_id=match.id, turning_point_id=tp_model.id, explanation_text=explanation_text)
    db.add(exp)
    match.status = "explained"
    db.commit()

    return ExplanationResponse(
        match_id=match_id,
        turning_point_index=turn_index,
        minute=tp.minute,
        explanation=explanation_text,
        causes=causes,
    )
