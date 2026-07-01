import pytest
import pandas as pd
from app.modules.momentum_detection import detect_turning_points


def make_features(minutes, scores):
    return pd.DataFrame({"minute": minutes, "momentum_score": scores})


def test_detects_sharp_shift():
    df = make_features([1, 2, 3, 4, 5], [0.0, 0.0, 0.5, 0.0, 0.0])
    tps = detect_turning_points(df, threshold=0.3)
    assert any(tp.minute == 2 for tp in tps)


def test_no_turning_points_on_flat():
    df = make_features([1, 2, 3, 4, 5], [0.1, 0.1, 0.1, 0.1, 0.1])
    tps = detect_turning_points(df, threshold=0.3)
    assert len(tps) == 0


def test_direction_home():
    df = make_features([1, 2, 3], [0.0, 0.5, 0.5])
    tps = detect_turning_points(df, threshold=0.3)
    assert tps[0].direction == "home"


def test_direction_away():
    df = make_features([1, 2, 3], [0.0, -0.5, -0.5])
    tps = detect_turning_points(df, threshold=0.3)
    assert tps[0].direction == "away"
