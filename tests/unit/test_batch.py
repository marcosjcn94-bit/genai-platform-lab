import json
from decimal import Decimal
from pathlib import Path


def test_fixture_has_schema_and_hand_calculated_results():
    fixture = json.loads(Path("data/fixtures/usage-v1.json").read_text(encoding="utf-8"))
    unique = {event["record_id"]: event for event in fixture["events"]}
    assert len(unique) == 3
    app_a = [event for event in unique.values() if event["application"] == "app-a"]
    assert sum(event["total_tokens"] for event in app_a) == 30
    assert sum(Decimal(event["spend"]) for event in app_a) == Decimal("0.3")
