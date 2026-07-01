import pytest
import pandas as pd
from app.modules.preprocessing import preprocess_events, assign_momentum_weight


def make_event(minute, etype, team, outcome=""):
    return {"minute": minute, "second": 0, "event_type": etype, "team": team, "player": "P", "outcome": outcome}


def test_positive_event_home():
    df = pd.DataFrame([make_event(10, "Shot", "Home")])
    result = preprocess_events(df, "Home")
    assert result.iloc[0]["weight"] > 0


def test_negative_event_home():
    df = pd.DataFrame([make_event(10, "Foul Committed", "Home")])
    result = preprocess_events(df, "Home")
    assert result.iloc[0]["weight"] < 0


def test_away_event_flipped():
    df = pd.DataFrame([make_event(10, "Shot", "Away")])
    result = preprocess_events(df, "Home")
    assert result.iloc[0]["weight"] < 0


def test_time_seconds():
    df = pd.DataFrame([make_event(5, "Shot", "Home")])
    df["second"] = 30
    result = preprocess_events(df, "Home")
    assert result.iloc[0]["time_seconds"] == 5 * 60 + 30
