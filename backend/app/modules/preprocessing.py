import pandas as pd
from sqlalchemy.orm import Session
from app.db.models import Event


# Events that contribute positively to momentum for the acting team
POSITIVE_EVENTS = {"Shot", "Goal", "Carry", "Dribble", "Key Pass"}
NEGATIVE_EVENTS = {"Foul Committed", "Yellow Card", "Red Card", "Dispossessed", "Error"}


def load_events_as_df(match_db_id: int, db: Session) -> pd.DataFrame:
    events = db.query(Event).filter(Event.match_id == match_db_id).order_by(Event.minute, Event.second).all()
    records = [
        {
            "minute": e.minute,
            "second": e.second or 0,
            "event_type": e.event_type,
            "team": e.team,
            "player": e.player,
            "outcome": e.outcome,
        }
        for e in events
    ]
    return pd.DataFrame(records)


def assign_momentum_weight(row: pd.Series) -> float:
    base = 0.0
    etype = row["event_type"]
    if etype in POSITIVE_EVENTS:
        base = 1.0
    elif etype in NEGATIVE_EVENTS:
        base = -1.0

    # Outcome modifiers
    outcome = str(row.get("outcome", ""))
    if "Successful" in outcome or "Complete" in outcome:
        base *= 1.2
    elif "Incomplete" in outcome or "Out" in outcome:
        base *= 0.5

    return base


def preprocess_events(df: pd.DataFrame, home_team: str) -> pd.DataFrame:
    df = df.copy()
    df["weight"] = df.apply(assign_momentum_weight, axis=1)
    # Flip sign for away team so home momentum is positive
    df.loc[df["team"] != home_team, "weight"] *= -1
    df["time_seconds"] = df["minute"] * 60 + df["second"]
    return df.sort_values("time_seconds").reset_index(drop=True)
