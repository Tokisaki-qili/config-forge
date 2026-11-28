"""model.py 的测试：只验「类型转换」，不验业务规则。

业务规则（范围、必填、枚举……）在 C1-1 的 validator 里测，别混进来。
"""

from datetime import datetime

from config_forge.model import (
    TIME_FORMAT,
    Activity,
    Item,
    RewardGroup,
    to_datetime,
    to_float,
    to_int,
)


# ---------- 转换函数 ----------


def test_to_int_accepts_spaces():
    assert to_int(" 5 ") == (5, None)


def test_to_int_rejects_garbage():
    value, err = to_int("abc")
    assert value is None
    assert err is not None
    assert "abc" in err


def test_to_float_ok():
    assert to_float("0.8") == (0.8, None)


def test_to_float_rejects_garbage():
    value, err = to_float("1.5x")
    assert value is None
    assert "1.5x" in err


def test_to_datetime_ok():
    value, err = to_datetime("2026-10-01T00:00:00")
    assert err is None
    assert value == datetime(2026, 10, 1, 0, 0, 0)


def test_to_datetime_bad_format():
    value, err = to_datetime("2026-10-01 00:00:00")  # 少个 T
    assert value is None
    assert "YYYY-MM-DDTHH:MM:SS" in err


# ---------- Item ----------


def test_item_from_row_ok():
    item, errors = Item.from_row(
        {"item_id": "IT-001", "name": "新手礼包", "quality": "common", "stack": "99"}
    )
    assert errors == []
    assert item is not None
    assert item.stack == 99
    assert item.name == "新手礼包"


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


# ---------- RewardGroup ----------


def test_reward_group_from_row_ok():
    group, errors = RewardGroup.from_row(
        {"group_id": "RG-01", "item_id": "IT-001", "count": "1"}
    )
    assert errors == []
    assert group is not None
    assert group.count == 1


def test_reward_group_bad_count():
    group, errors = RewardGroup.from_row(
        {"group_id": "RG-02", "item_id": "IT-002", "count": "两颗"}
    )
    assert group is None
    assert any("count" in e for e in errors)


# ---------- Activity ----------


def _activity_row(**overrides: str) -> dict[str, str]:
    row = {
        "activity_id": "ACT-0001",
        "name": "国庆签到",
        "type": "festival",
        "start_time": "2026-10-01T00:00:00",
        "end_time": "2026-10-07T23:59:59",
        "reward_group": "RG-01",
        "weight": "0.8",
        "max_claims": "1",
        "min_level": "10",
        "status": "live",
    }
    row.update(overrides)
    return row


def test_activity_from_row_ok():
    activity, errors = Activity.from_row(_activity_row())
    assert errors == []
    assert activity is not None
    assert activity.name == "国庆签到"  # 中文不乱码
    assert activity.start_time == datetime(2026, 10, 1)
    assert activity.weight == 0.8


def test_activity_bad_datetime():
    activity, errors = Activity.from_row(_activity_row(end_time="2026-10-07T24:00:00"))
    assert activity is None
    assert any("end_time" in e for e in errors)


def test_activity_zero_max_claims_is_valid():
    # max_claims=0 是"不能领取"的合法业务值，模型层不许拦
    activity, errors = Activity.from_row(_activity_row(max_claims="0"))
    assert errors == []
    assert activity is not None
    assert activity.max_claims == 0


def test_activity_negative_level_is_valid():
    # 负数能转成 -1；它合不合法是 R04 的事
    activity, errors = Activity.from_row(_activity_row(min_level="-1"))
    assert errors == []
    assert activity is not None
    assert activity.min_level == -1


def test_activity_empty_name_is_accepted():
    # 空名字在模型层照样能构造；"必填"是 R01 的事
    activity, errors = Activity.from_row(_activity_row(name=""))
    assert errors == []
    assert activity is not None
    assert activity.name == ""


def test_activity_reports_all_bad_fields_at_once():
    activity, errors = Activity.from_row(
        _activity_row(weight="1.5x", max_claims="很多", min_level="")
    )
    assert activity is None
    assert len(errors) == 3  # 三个字段一起报，不是遇到第一个就返回
