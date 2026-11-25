from dataclasses import dataclass
from datetime import datetime

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

def to_int(raw : str) -> tuple[int | None, str | None]:
    try:
        return int(raw.strip()), None
    except ValueError:
        return None, f"不是整数:{raw.strip()!r}"

def to_float(raw : str) -> tuple[float | None, str | None]:
    try:
        return float(raw.strip()), None
    except ValueError:
        return None, f"不是小数:{raw.strip()!r}"

def to_datetime(raw : str) -> tuple[datetime | None, str | None]:
    try:
        return datetime.strptime(raw.strip(), TIME_FORMAT), None
    except ValueError:
        return None, f"不是合法时间(要 YYYY-MM-DDTHH:MM:SS):{raw.strip()!r}"

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
