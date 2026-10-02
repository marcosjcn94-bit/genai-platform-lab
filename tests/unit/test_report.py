from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest

from scripts.report import aggregate, collect

START = datetime(2026, 1, 1, tzinfo=UTC)
END = datetime(2026, 1, 2, tzinfo=UTC)


def row(identifier, timestamp="2026-01-01T12:00:00Z", **changes):
    return {
        "request_id": identifier,
        "startTime": timestamp,
        "api_key": "hash-a",
        "model": "primary",
        "prompt_tokens": 8,
        "completion_tokens": 4,
        "total_tokens": 12,
        "spend": "0.10",
        "status": "success",
        "endTime": "2026-01-01T12:00:01Z",
    } | changes


def test_pagination_ignores_capped_totals_deduplicates_and_filters_utc():
    pages = [
        [row("one"), row("before", "2025-12-31T23:59:59Z")],
        [row("one"), row("two", api_key="hash-b", spend=None)],
        [row("end", "2026-01-02T00:00:00Z")],
        [],
    ]
    requested = []

    def server(req):
        page = int(req.url.params["page"])
        requested.append(page)
        return httpx.Response(200, json={"data": pages[page - 1], "total_pages": 1})

    with httpx.Client(base_url="http://gateway", transport=httpx.MockTransport(server)) as client:
        events = collect(client, START, END, {"hash-a": "app-a", "hash-b": "app-b"})
    assert requested == [1, 2, 3, 4]
    assert [e["record_id"] for e in events] == ["one", "two"]
    assert events[1]["spend"] is None
    assert events[0]["duration_ms"] == 1000
    assert "api_key" not in events[0]


def test_missing_values_and_decimal_coverage():
    events = [
        {
            "application": "app-a",
            "model": "primary",
            "spend": "0.1",
            "total_tokens": 12,
            "prompt_tokens": 8,
            "completion_tokens": 4,
            "status": "success",
            "duration_ms": 1000,
        },
        {
            "application": "app-a",
            "model": "primary",
            "spend": "0.2",
            "total_tokens": None,
            "prompt_tokens": None,
            "completion_tokens": None,
            "status": None,
            "duration_ms": None,
        },
        {
            "application": "app-a",
            "model": "primary",
            "spend": None,
            "total_tokens": None,
            "prompt_tokens": None,
            "completion_tokens": None,
            "status": None,
            "duration_ms": None,
        },
    ]
    result = aggregate(events)[0]
    assert Decimal(result["spend"]) == Decimal("0.3")
    assert result["spend_known"] == 2
    assert result["total_tokens"] == 12
    assert result["total_tokens_known"] == 1
    assert result["status_known"] == 1
    assert result["requests"] == 3


def test_source_failure_does_not_become_empty_success():
    with httpx.Client(
        base_url="http://gateway", transport=httpx.MockTransport(lambda req: httpx.Response(503))
    ) as client:
        with pytest.raises(httpx.HTTPStatusError):
            collect(client, START, END, {})


def test_unknown_identity_is_not_silently_attributed():
    pages = [[row("one", api_key="unknown")], []]
    with httpx.Client(
        base_url="http://gateway",
        transport=httpx.MockTransport(
            lambda req: httpx.Response(200, json={"data": pages[int(req.url.params["page"]) - 1]})
        ),
    ) as client:
        events = collect(client, START, END, {})
    assert events[0]["application"] == "unattributed"


def test_repeated_page_stops_instead_of_infinite_export():
    with httpx.Client(
        base_url="http://gateway",
        transport=httpx.MockTransport(lambda req: httpx.Response(200, json={"data": [row("one")]})),
    ) as client:
        with pytest.raises(ValueError):
            collect(client, START, END, {})
