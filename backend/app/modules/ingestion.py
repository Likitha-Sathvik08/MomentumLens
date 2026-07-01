import json
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.models import Match, Event


def load_match_from_json(filepath: str, db: Session) -> Match:
    path = Path(filepath)
    with open(path) as f:
        data = json.load(f)

    match = Match(
        match_id=data["match_id"],
        home_team=data["home_team"],
        away_team=data["away_team"],
        date=data.get("date"),
        competition=data.get("competition"),
    )
    db.add(match)
    db.flush()

    for evt in data.get("events", []):
        event = Event(
            match_id=match.id,
            minute=evt["minute"],
            second=evt.get("second"),
            event_type=evt["type"],
            team=evt.get("team"),
            player=evt.get("player"),
            outcome=evt.get("outcome"),
            extra=evt.get("extra"),
        )
        db.add(event)

    db.commit()
    db.refresh(match)
    return match


def load_match_from_statsbomb(events_df: pd.DataFrame, match_meta: dict, db: Session) -> Match:
    """Load from a StatsBomb-format DataFrame (open data compatible)."""
    match = Match(
        match_id=str(match_meta["match_id"]),
        home_team=match_meta["home_team"],
        away_team=match_meta["away_team"],
        date=str(match_meta.get("match_date", "")),
        competition=match_meta.get("competition", ""),
    )
    db.add(match)
    db.flush()

    for _, row in events_df.iterrows():
        event = Event(
            match_id=match.id,
            minute=int(row.get("minute", 0)),
            second=int(row.get("second", 0)),
            event_type=str(row.get("type", "")),
            team=str(row.get("team", "")),
            player=str(row.get("player", "")),
            outcome=str(row.get("outcome", "")) if pd.notna(row.get("outcome")) else None,
            extra={},
        )
        db.add(event)

    db.commit()
    db.refresh(match)
    return match


def load_match_from_dict(data: dict, db: Session) -> Match:
    """Load a match and its events from a parsed dictionary (API payload or parsed JSON file)."""
    existing = db.query(Match).filter(Match.match_id == data["match_id"]).first()
    if existing:
        return existing

    match = Match(
        match_id=data["match_id"],
        home_team=data["home_team"],
        away_team=data["away_team"],
        date=data.get("date"),
        competition=data.get("competition"),
    )
    db.add(match)
    db.flush()

    for evt in data.get("events", []):
        # Support both "type" key (from JSON files) and "event_type" key
        event_type = evt.get("type") or evt.get("event_type", "")
        event = Event(
            match_id=match.id,
            minute=evt.get("minute", 0),
            second=evt.get("second", 0),
            event_type=event_type,
            team=evt.get("team"),
            player=evt.get("player"),
            outcome=evt.get("outcome"),
            extra=evt.get("extra"),
        )
        db.add(event)

    db.commit()
    db.refresh(match)
    return match
