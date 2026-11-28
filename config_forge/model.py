"""数据模型层：把 loader 读出来的字符串行，转成带类型的对象。

职责边界（重要）：
- 这里只管「能不能转换成 int / float / datetime」
- **不管**「这个数字大小对不对」「这个字段能不能为空」——那些是规则层（R01/R04/R06...）的事
- 坏值不抛异常，返回 (None, [错误说明])，让上层决定是跳过这一行还是整表停下
"""

from dataclasses import dataclass
from datetime import datetime

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def to_int(raw: str) -> tuple[int | None, str | None]:
    """'5' -> (5, None)；'abc' -> (None, '不是整数：abc')"""
    try:
        return int(raw.strip()), None
    except ValueError:
        return None, f"不是整数：{raw.strip()!r}"


def to_float(raw: str) -> tuple[float | None, str | None]:
    """'0.8' -> (0.8, None)；'abc' -> (None, '不是小数：abc')"""
    try:
        return float(raw.strip()), None
    except ValueError:
        return None, f"不是小数：{raw.strip()!r}"


def to_datetime(raw: str) -> tuple[datetime | None, str | None]:
    """'2026-10-01T00:00:00' -> (datetime, None)；格式差一位就返回错误"""
    try:
        return datetime.strptime(raw.strip(), TIME_FORMAT), None
    except ValueError:
        return None, f"不是合法时间（要 YYYY-MM-DDTHH:MM:SS）：{raw.strip()!r}"


@dataclass
class Item:
    item_id: str
    name: str
    quality: str
    stack: int

    @classmethod
    def from_row(cls, row: dict[str, str]) -> tuple["Item | None", list[str]]:
        errors: list[str] = []

        stack, err = to_int(row.get("stack", ""))
        if err is not None:
            errors.append(f"stack {err}")

        if errors:
            return None, errors

        assert stack is not None
        return cls(
            item_id=row.get("item_id", "").strip(),
            name=row.get("name", "").strip(),
            quality=row.get("quality", "").strip(),
            stack=stack,
        ), []


@dataclass
class RewardGroup:
    group_id: str
    item_id: str
    count: int

    @classmethod
    def from_row(cls, row: dict[str, str]) -> tuple["RewardGroup | None", list[str]]:
        errors: list[str] = []

        count, err = to_int(row.get("count", ""))
        if err is not None:
            errors.append(f"count {err}")

        if errors:
            return None, errors

        assert count is not None
        return cls(
            group_id=row.get("group_id", "").strip(),
            item_id=row.get("item_id", "").strip(),
            count=count,
        ), []


@dataclass
class Activity:
    activity_id: str
    name: str
    type: str
    start_time: datetime
    end_time: datetime
    reward_group: str
    weight: float
    max_claims: int
    min_level: int
    status: str

    @classmethod
    def from_row(cls, row: dict[str, str]) -> tuple["Activity | None", list[str]]:
        errors: list[str] = []

        start_time, err = to_datetime(row.get("start_time", ""))
        if err is not None:
            errors.append(f"start_time {err}")

        end_time, err = to_datetime(row.get("end_time", ""))
        if err is not None:
            errors.append(f"end_time {err}")

        weight, err = to_float(row.get("weight", ""))
        if err is not None:
            errors.append(f"weight {err}")

        max_claims, err = to_int(row.get("max_claims", ""))
        if err is not None:
            errors.append(f"max_claims {err}")

        min_level, err = to_int(row.get("min_level", ""))
        if err is not None:
            errors.append(f"min_level {err}")

        if errors:
            return None, errors

        assert start_time is not None
        assert end_time is not None
        assert weight is not None
        assert max_claims is not None
        assert min_level is not None
        return cls(
            activity_id=row.get("activity_id", "").strip(),
            name=row.get("name", "").strip(),
            type=row.get("type", "").strip(),
            start_time=start_time,
            end_time=end_time,
            reward_group=row.get("reward_group", "").strip(),
            weight=weight,
            max_claims=max_claims,
            min_level=min_level,
            status=row.get("status", "").strip(),
        ), []
