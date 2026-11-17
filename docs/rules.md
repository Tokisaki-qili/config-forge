# 规则清单（12 条，全部要由 `rules.yaml` 驱动）

> 核心验收：**加一条规则只改 YAML，不改 Python 代码。**

## 级别

| 级别 | 含义 | 例子 |
|---|---|---|
| `error` | 绝对不能进引擎，必须改 | 外键指向不存在的道具 |
| `warn` | 能进，但策划该看一眼 | 活动权重过强、奖励组被反复复用 |

## 规则

| ID | kind | 目标 | 条件 | 级别 | 期望报错文案（示例） |
|---|---|---|---|---|---|
| R01 | `required` | 各表非空列 | 值缺失或空字符串 | error | `activities 第 3 行：name 不能为空` |
| R02 | `type` | 各表声明列 | 无法转换为声明类型 | error | `activities 第 4 行：weight=「1.5x」不是合法小数` |
| R03 | `regex` | `activities.activity_id`、`items.item_id` | 不匹配 `^ACT-\d{4}$` / `^IT-\d{3}$` | error | `activities 第 5 行：activity_id=「ACT5」不符合格式 ACT-0001` |
| R04 | `range` | `activities.weight` / `max_claims` / `min_level`；`reward_groups.count`；`items.stack` | 超出闭区间 | error | `activities 第 4 行：weight=1.5 超出范围 [0.0, 1.0]` |
| R05 | `length` | `activities.name`(1–40)、`items.name`(1–30) | 长度越界 | error | `activities 第 3 行：name 长度 0，应在 [1, 40]` |
| R06 | `enum` | `type` / `status` / `quality` | 不在允许值集合 | error | `activities 第 4 行：status=「online」不在 [draft, review, live, offline]` |
| R07 | `unique` | `activities.activity_id`；`reward_groups.(group_id,item_id)` | 重复出现 | error | `reward_groups 第 5 行：group_id=RG-01 + item_id=IT-001 重复（首次出现在第 1 行）` |
| R08 | `table_unique` | `items.item_id` | 重复 | error | `items 第 6 行：item_id=IT-001 重复` |
| R09 | `datetime_order` | `activities.start_time` / `end_time` | `end_time <= start_time` | error | `activities 第 3 行：end_time(2026-10-04) 早于 start_time(2026-10-05)` |
| R10 | `foreign_key` | `activities.reward_group`；`reward_groups.item_id` | 目标表不存在该键 | error | `activities 第 3 行：reward_group=RG-09 在 reward_groups 中不存在` |
| R11 | `overlap` | `activities`（同 `type`，状态 ∈ {review, live}） | 两个活动时间区间重叠 | error | `ACT-0001 与 ACT-0004 同为 festival 且时间重叠 2026-10-01~2026-10-07` |
| R12 | `soft_threshold` | `activities.weight` | `weight >= 0.95` 且 `type != festival` | warn | `activities 第 2 行：非节日活动 weight=0.98，体验过强，确认是否刻意` |

## 文案要求

1. **说清是哪张表第几行（或主键）、哪个字段、什么值、期望什么**。只报 "invalid" 的报错等于没报。
2. 不要暴露 Python 异常栈给策划；异常只在日志里。
3. 一个字段多条规则命中时，按 R01→R02→R06→R04→R05 的顺序报，**别刷屏**（同一字段同类错误只报第一条）。
4. 报告结尾给一行汇总：`3 张表 / 5 条记录 / error 8 / warn 1`。

## 规则文件格式（`config/rules.yaml`）

见 [rules.example.yaml](D:\蓝色大肥鱼\projects\config-forge\config\rules.example.yaml)，它只给了 3 条（覆盖 `required` / `range` / `unique` 三种 kind）。
**剩下 9 条由你按上表补全。** 每条规则必须带 `id` / `kind` / `table` / `level` / `message` 字段，message 里用 `{record}` `{field}` `{value}` 占位。
