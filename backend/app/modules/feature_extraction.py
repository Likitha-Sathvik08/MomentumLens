import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Feature


def extract_features(preprocessed_df: pd.DataFrame, match_db_id: int, window: int = 5) -> pd.DataFrame:
    """Compute per-minute rolling features from preprocessed events."""
    df = preprocessed_df.copy()
    minutes = range(int(df["minute"].max()) + 1)
    records = []

    for minute in minutes:
        window_df = df[(df["minute"] >= minute - window) & (df["minute"] <= minute)]
        if window_df.empty:
            records.append({"minute": minute, "momentum_score": 0.0, "pressure_index": 0.0,
                            "shots_home": 0, "shots_away": 0, "possession_home": 50.0})
            continue

        momentum = float(window_df["weight"].sum())
        shots_home = int(window_df[(window_df["event_type"] == "Shot") & (window_df["weight"] > 0)].shape[0])
        shots_away = int(window_df[(window_df["event_type"] == "Shot") & (window_df["weight"] < 0)].shape[0])

        total_events = max(len(window_df), 1)
        home_events = window_df[window_df["weight"] > 0].shape[0]
        possession_home = round((home_events / total_events) * 100, 2)

        # Pressure = event density in window
        pressure = round(len(window_df) / window, 2)

        records.append({
            "minute": minute,
            "momentum_score": momentum,
            "shots_home": shots_home,
            "shots_away": shots_away,
            "possession_home": possession_home,
            "pressure_index": pressure,
        })

    return pd.DataFrame(records)


def save_features(features_df: pd.DataFrame, match_db_id: int, db: Session):
    for _, row in features_df.iterrows():
        feat = Feature(
            match_id=match_db_id,
            minute=int(row["minute"]),
            momentum_score=float(row["momentum_score"]),
            shots_home=int(row["shots_home"]),
            shots_away=int(row["shots_away"]),
            possession_home=float(row["possession_home"]),
            pressure_index=float(row["pressure_index"]),
        )
        db.add(feat)
    db.commit()
