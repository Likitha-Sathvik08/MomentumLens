import pandas as pd
from app.models.schemas import CauseRanking


CAUSE_EVENT_MAP = {
    "substitution": ["Substitution"],
    "red_card": ["Red Card"],
    "yellow_card": ["Yellow Card"],
    "goal": ["Goal"],
    "high_pressure": ["Pressure", "Ball Recovery", "Tackle"],
    "possession_shift": ["Carry", "Dribble", "Dispossessed"],
}


def rank_causes(
    preprocessed_df: pd.DataFrame,
    turning_point_minute: int,
    window: int = 5,
) -> list[CauseRanking]:
    """Return ranked causes for a turning point at the given minute."""
    tp_window = preprocessed_df[
        (preprocessed_df["minute"] >= turning_point_minute - window)
        & (preprocessed_df["minute"] <= turning_point_minute)
    ]

    rankings: list[CauseRanking] = []

    for cause, event_types in CAUSE_EVENT_MAP.items():
        matching = tp_window[tp_window["event_type"].isin(event_types)]
        if matching.empty:
            continue

        score = round(abs(matching["weight"].sum()), 4)
        evidence = []
        for _, row in matching.iterrows():
            player = row.get("player", "Unknown")
            team = row.get("team", "")
            evidence.append(f"min {row['minute']}: {row['event_type']} by {player} ({team})")

        rankings.append(CauseRanking(cause=cause, score=score, evidence=evidence[:5]))

    rankings.sort(key=lambda x: x.score, reverse=True)
    return rankings
