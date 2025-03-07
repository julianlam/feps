from datetime import date, timedelta

from .issue import parse_and_update_date_received, create_body


def test_parse_and_update_date_received():
    today = date.today()
    result = parse_and_update_date_received(today.isoformat())

    assert result == today


def test_parse_and_update_date_received_parse_error():
    today = date.today()
    result = parse_and_update_date_received("incorrect")

    assert result == today


def test_parse_and_update_date_received_outdated():
    today = date.today()
    result = parse_and_update_date_received((today - timedelta(days=60)).isoformat())

    assert result == today


def test_create_body():
    result = create_body("fep-0000.md", date(2025, 2, 8))

    assert (
        result
        == """
The [proposal](https://codeberg.org/fediverse/fep/src/branch/main/fep-0000.md) has been received. Thank you!

This issue tracks discussions and updates to the proposal during the `DRAFT` period.

Please post links to relevant discussions as comments to this issue.

`dateReceived`: 2025-02-08

If no further actions are taken, the proposal may be set by the facilitators to `WITHDRAWN` on 2026-02-08 (in 1 year).
"""
    )
