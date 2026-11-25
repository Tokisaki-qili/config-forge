from pathlib import Path

import pytest

from config_forge.model import to_int, to_datetime

ROOT = Path(__file__).resolve().parent.parent

def test_to_int():
    assert to_int(" 5 ") == (5, None)
    assert to_int("abc")[0] is None


def test_to_datetime_bad_format():
    value, err = to_datetime("2026-10-01 00:00:00")
    assert value is None
    assert err is not None

from config_forge.model import Item, to_datetime, to_int


def test_item_from_row_ok():
    item, errors = Item.from_row(
        {"item_id": "IT-001", "name": "新手礼包", "quality": "common", "stack": "99"}
    )
    assert errors == []
    assert item is not None
    assert item.stack == 99


def test_item_bad_int_returns_error():
    item, errors = Item.from_row(
        {"item_id": "IT-002", "name": "破损道具", "quality": "common", "stack": "abc"}
    )
    assert item is None
    assert len(errors) == 1
    assert "stack" in errors[0]


def test_item_zero_stack_is_valid():
    item, errors = Item.from_row(
        {"item_id": "IT-003", "name": "零堆叠", "quality": "common", "stack": "0"}
    )
    assert errors == []
    assert item is not None
    assert item.stack == 0
