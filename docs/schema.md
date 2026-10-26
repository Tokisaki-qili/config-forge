# 数据契约（schema）

三张表，存在 `data/*.csv`。所有表都是 UTF-8 无 BOM、逗号分隔、第一行是表头。

## 1. `activities.csv` — 活动主表

| 列 | 类型 | 含义 | 示例 |
|---|---|---|---|
| `activity_id` | string | 主键，格式 `ACT-` + 4 位数字 | `ACT-0001` |
| `name` | string | 活动名，1–40 字，不能为空 | `国庆签到` |
| `type` | enum | `daily_week` / `season` / `festival` / `event` | `festival` |
| `start_time` | datetime | ISO 8601，`YYYY-MM-DDTHH:MM:SS` | `2026-10-01T00:00:00` |
| `end_time` | datetime | 必须晚于 `start_time` | `2026-10-07T23:59:59` |
| `reward_group` | string | 外键 → `reward_groups.group_id` | `RG-01` |
| `weight` | float | 活动权重，0.0–1.0 | `0.8` |
| `max_claims` | int | 最多领取次数，1–100 | `5` |
| `min_level` | int | 参与等级下限，1–80 | `1` |
| `status` | enum | `draft` / `review` / `live` / `offline` | `live` |

## 2. `reward_groups.csv` — 奖励组明细

| 列 | 类型 | 含义 | 示例 |
|---|---|---|---|
| `group_id` | string | 奖励组 id，多行同组 = 一组多件奖励 | `RG-01` |
| `item_id` | string | 外键 → `items.item_id` | `IT-001` |
| `count` | int | 数量，1–999 | `5` |

`(group_id, item_id)` 组合唯一（同一组里同一件道具不能出现两次）。

## 3. `items.csv` — 道具表

| 列 | 类型 | 含义 | 示例 |
|---|---|---|---|
| `item_id` | string | 主键，格式 `IT-` + 3 位数字 | `IT-001` |
| `name` | string | 道具名，1–30 字 | `新手礼包` |
| `quality` | enum | `common` / `rare` / `epic` | `common` |
| `stack` | int | 堆叠上限，1–99999 | `99` |

## 契约细节（会被 review 的点）

1. **类型转换失败不是崩溃**：`weight=abc` 要收集成「解析错误」，继续处理下一行。一行坏，不能拖垮整张表。
2. **列缺失/列多余**：缺列 = 致命错误（这张表没法用）；多余列 = 警告。
3. **空表**：0 行数据是合法输入（但要能跑完，不崩）。
4. **换行与尾随空格**：CSV 里 `"国庆签到, 限时"` 这种带逗号的值是合法的，值前后的空格要 trim。
5. **中文**：Windows 控制台默认 GBK，输出中文前要处理编码（`sys.stdout.reconfigure(encoding="utf-8")` 或设环境变量），否则乱码。
