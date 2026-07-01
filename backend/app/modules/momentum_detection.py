import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import TurningPoint as TurningPointModel
from app.models.schemas import TurningPoint
from app.core.config import settings


def detect_turning_points(features_df: pd.DataFrame, threshold: float = None) -> list[TurningPoint]:
    threshold = threshold or settings.turning_point_threshold
    scores = features_df["momentum_score"].values
    minutes = features_df["minute"].values
    turning_points = []

    for i in range(1, len(scores) - 1):
        delta = scores[i] - scores[i - 1]
        if abs(delta) >= threshold:
            direction = "home" if delta > 0 else "away"
            # Confidence: normalize delta relative to observed max swing
            max_swing = max(abs(scores).max(), 1e-6)
            confidence = round(min(abs(delta) / max_swing, 1.0), 3)
            turning_points.append(
                TurningPoint(
                    minute=int(minutes[i]),
                    momentum_delta=round(float(delta), 4),
                    direction=direction,
                    confidence=confidence,
                )
            )

    return turning_points


def save_turning_points(turning_points: list[TurningPoint], match_db_id: int, db: Session) -> list[TurningPointModel]:
    saved = []
    for tp in turning_points:
        model = TurningPointModel(
            match_id=match_db_id,
            minute=tp.minute,
            momentum_delta=tp.momentum_delta,
            direction=tp.direction,
            confidence=tp.confidence,
        )
        db.add(model)
        db.flush()
        saved.append(model)
    db.commit()
    return saved
