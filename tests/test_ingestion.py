import pytest
import json
from pathlib import Path
from app.modules.ingestion import load_match_from_dict, load_match_from_json
from app.db.models import Match, Event


def test_load_match_from_dict(test_db):
    data = {
        "match_id": "test_m1",
        "home_team": "Home",
        "away_team": "Away",
        "events": [
            {"minute": 1, "type": "Shot", "team": "Home"},
            {"minute": 2, "type": "Pass", "team": "Away"}
        ]
    }
    
    match = load_match_from_dict(data, test_db)
    
    assert match.match_id == "test_m1"
    assert match.home_team == "Home"
    
    # Check events were loaded
    events = test_db.query(Event).filter(Event.match_id == match.id).all()
    assert len(events) == 2
    assert events[0].event_type == "Shot"
    assert events[1].team == "Away"


def test_load_sample_json(test_db):
    sample_path = Path(__file__).parent.parent / "data" / "sample" / "sample_match.json"
    
    match = load_match_from_json(str(sample_path), test_db)
    
    assert match.match_id == "match_sample_001"
    events = test_db.query(Event).filter(Event.match_id == match.id).all()
    assert len(events) == 18  # The sample has 18 events
