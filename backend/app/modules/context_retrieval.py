from pathlib import Path
from app.models.schemas import TurningPoint, CauseRanking


TACTICS_KB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "sample" / "tactics_kb.txt"


def load_knowledge_base() -> str:
    if TACTICS_KB_PATH.exists():
        return TACTICS_KB_PATH.read_text(encoding="utf-8")
    return ""


def build_context(
    turning_point: TurningPoint,
    causes: list[CauseRanking],
    home_team: str,
    away_team: str,
) -> str:
    """Build a structured context string for the Granite prompt."""
    top_causes = causes[:3]
    cause_lines = "\n".join(
        f"- {c.cause.replace('_', ' ').title()} (score: {c.score}): {'; '.join(c.evidence[:2])}"
        for c in top_causes
    )

    direction_team = home_team if turning_point.direction == "home" else away_team

    context = f"""
Match: {home_team} vs {away_team}
Turning Point: Minute {turning_point.minute}
Momentum shifted toward: {direction_team} (delta={turning_point.momentum_delta:+.3f}, confidence={turning_point.confidence})

Top Ranked Causes:
{cause_lines}
""".strip()

    kb = load_knowledge_base()
    if kb:
        context += f"\n\nTactical Reference:\n{kb[:800]}"

    return context
