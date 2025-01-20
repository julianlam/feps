from datetime import date, timedelta

from .issue import parse_and_update_date_received


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
