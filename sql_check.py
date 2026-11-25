# -*- coding: utf-8 -*-
"""用 SQL 复核 config-forge 的校验结果：同一批数据，两套查法对账。

用法：python sql_check.py
输出：每类问题查出的行数与具体行号，供和 Python 脚本（loader.py）的结果对照。
"""
import csv
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


def load(conn):
    for name in ("activities", "items", "reward_groups"):
        path = DATA / f"{name}.csv"
        with path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys())
        conn.execute(f"CREATE TABLE {name} ({', '.join(c + ' TEXT' for c in cols)})")
        conn.executemany(
            f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})",
            [[r[c] for c in cols] for r in rows],
        )
    conn.commit()


CHECKS = {
    "缺字段（姓名为空）": "SELECT rowid FROM activities WHERE name IS NULL OR name = ''",
    "缺字段（奖励组为空）": "SELECT rowid FROM activities WHERE reward_group IS NULL OR reward_group = ''",
    "重复 item_id": "SELECT item_id FROM items GROUP BY item_id HAVING COUNT(*) > 1",
    "奖励组引用不存在的活动组": (
        "SELECT a.rowid, a.reward_group FROM activities a "
        "LEFT JOIN reward_groups g ON a.reward_group = g.group_id "
        "WHERE a.reward_group IS NOT NULL AND a.reward_group != '' AND g.group_id IS NULL"
    ),
    "奖励组引用不存在的道具": (
        "SELECT g.rowid, g.item_id FROM reward_groups g "
        "LEFT JOIN items i ON g.item_id = i.item_id WHERE i.item_id IS NULL"
    ),
    "活动时间重叠": (
        "SELECT a.rowid, b.rowid FROM activities a JOIN activities b "
        "ON a.rowid < b.rowid AND a.start_time < b.end_time AND b.start_time < a.end_time"
    ),
}


def main():
    conn = sqlite3.connect(":memory:")
    load(conn)
    total = 0
    for label, sql in CHECKS.items():
        rows = conn.execute(sql).fetchall()
        total += len(rows)
        print(f"[{label}] {len(rows)} 处")
        for row in rows[:5]:
            print("   ", row)
    print(f"合计 {total} 处")


if __name__ == "__main__":
    main()
