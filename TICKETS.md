# 任务板：config-forge（组长派单）

> 目标岗位：**技术策划（Technical Designer）**。这几周你写的每一个模块，都要能回答一个问题：
> **"策划为什么愿意用你这个小工具，而不是继续手改 Excel？"** 答不上来的功能，砍掉。

---

## 0. 这个项目在简历上的位置

| 项目 | 角色 | 讲什么 |
|---|---|---|
| `game-npc-agent` | 已完成，冻结 | AI 决策层的工程取舍（降级、校验、延迟） |
| **`config-forge`** | **主线** | 工具链思维：生成 → 校验 → 报错 → 导回引擎 |
| UE5 灰盒 demo | 补充（Sprint 5 之后） | 证明你能进引擎，不只会在命令行 |

三者共用一条叙事：**"把 AI 塞进游戏生产管线，并且让它出错时不出事故。"**

---

## 1. 规矩（在 game-systems-lab 基础上加三条）

1. 每个 ticket 一个 commit，信息格式：`C1-1 校验引擎：规则驱动 + 20 断言`
2. 交付附三样：跑的命令 / 测试输出 / **100 字自我 review**（哪里写丑、复杂度、下次改什么）
3. 每个 ticket ≥ 声明的断言数，必须覆盖空输入、坏输入、重复输入
4. **加规则不许改 Python**（Sprint 1 起是硬验收）——做不到就是设计错了，重写
5. **报错文案必须让策划看懂**：说清表、行、字段、值、期望。只写 "invalid" 算没写
6. **AI 用在哪要留痕**：`AI_USAGE.md` 记下每次用 AI 生成了什么、你改了什么、为什么（面试会问）
7. 不许 import 第三方校验库（pydantic / jsonschema / cerberus / pandas.apply 校验），核心逻辑手写

---

## 2. 岗位能力映射（每条 ticket 都在补一个真实要求）

| 技术策划 JD 要求 | 你在这里补 |
|---|---|
| 熟悉配置表结构、能设计字段 | `docs/schema.md` + `schema.yaml` |
| 会用脚本做工具（Python/C#/TS 至少一） | 整个项目 |
| 能做数据校验、保证配置质量 | 校验引擎 + 报告 |
| 能跟策划/程序沟通，把需求翻译成规格 | 报错文案 + Markdown 报告 + 100 字说明 |
| 有 AI 工具使用经验，能甄别 AI 输出 | LLM 生成层 + 错误分布统计 |
| 了解引擎数据导入流程 | UE DataTable 导出 + 灰盒 demo |

---

## 3. Sprint 总览

| Sprint | 时长 | 主题 | 交付物（能演示的东西） |
|---|---|---|---|
| 0 | 3–4 天 | 骨架与数据契约 | `python -m config_forge.cli` 能读三张表并报行数 |
| 1 | 5 天 | 校验引擎 v1 | 12 条规则驱动，`report.json` 出结果 |
| 2 | 5 天 | 关系与冲突 | 外键 + 时间重叠 + 给策划看的 Markdown 报告 |
| 3 | 4 天 | AI 生成层 | 一句需求 → 草稿配置（无 key 也能跑） |
| 4 | 4 天 | 度量（简历数字来源） | `report/metrics.md`：首次通过率 + 错误分布 |
| 5 | 5 天 | 引擎闭环 | UE DataTable 可导入 + 一行驱动的蓝图片段 |
| 6 | 3 天 | 演示与包装 | 5 分钟 demo 脚本 + README + 简历 bullet |

**时间盒纪律**：超时优先砍功能，不许砍测试。Sprint 0-1 两周内必须结束。

---

## 4. Sprint 0 · 骨架与数据契约（本周）

> 如果看完任务板还不知道这项目在干嘛，先看 [docs/一分钟看懂.md](D:\蓝色大肥鱼\projects\config-forge\docs\一分钟看懂.md)。

### C0-0 人肉校验（30 分钟，不写代码）
拿 `data/` 下三张表，用眼睛和脑子把错找出来，写在纸上。目标：至少 6 条，每条写清「哪张表、哪一行、哪个字段、错在哪」。
**做完你手上就有了一份"标准答案"**——之后程序跑出来的结果跟这张纸对不上，就是程序错了。
交付：抄进 `docs/人手校验记录.md`（拍照也行）。

### C0-1 读得进来（2 天）
**目标**：能读 schema + 三张 CSV，打印每张表的行数和列数。

**要做**：
- `config_forge/loader.py`
  - `load_schema(path) -> dict`：读 `config/schema.yaml`，校验 `version` 存在、每张表有 `file` 和 `columns`
  - `load_table(name, spec, data_dir) -> LoadResult`，`LoadResult` 里有 `records: list[dict]` 和 `errors: list[ParseError]`
  - `ParseError` 至少含 `file / line_no / column / raw_value / message`
- `config_forge/cli.py`：`--schema`、`--data`、`--out` 三个参数；**先只做到打印统计**
- `config_forge/__init__.py` 留空或放 `__version__`

**契约细节**：
- 缺列 → 抛 `SchemaError`（这是配置契约错误，属于程序员该修的 bug，不是数据错误）
- 多余列 → 收进 `errors`，级别 warn
- 空文件 / 只有表头 → 合法，0 行
- 值去首尾空格；`"a,b"` 这种带逗号的值必须正确解析（用 `csv` 模块，别 `split(",")`）

**验收（5 条断言）**：读三张表行数分别为 5 / 5 / 3；缺列抛 `SchemaError`；坏 CSV 行进 `errors` 不崩；空文件返回 0 行；中文表头不乱码。

**我会挑的地方**：`except Exception: pass` 直接判不合格；错误信息里没有行号也不合格。

### C0-2 数据模型与类型转换（1.5 天）
**目标**：把字符串行转成带类型的对象，坏值不崩。

**要做**：
- `config_forge/model.py`：`@dataclass Activity / RewardGroup / Item`，字段类型按 `docs/schema.md`
- 每个类有 `from_row(row) -> tuple[Optional[Self], list[str]]`：成功返回 (对象, [])，失败返回 (None, ["weight 不是合法小数：'1.5x'"])
- `datetime` 用 `strptime("%Y-%m-%dT%H:%M:%S")`，解析失败走上面那条路

**验收（8 条断言）**：正常行转换成功；`weight=abc` 返回错误不抛；`max_claims=0` 能转成 0（**范围是规则层的事，模型层不管**）；空字符串字段；中文名；时间格式差一位；int 带空格；负数能转（范围交给 R04）。

**我会挑的地方**：模型层偷偷做业务校验 = 职责混乱。**模型只管类型，规则只管业务。**

---

## 5. Sprint 1 · 校验引擎 v1（下周 5 天）

### C1-1 规则驱动（3 天）
**目标**：`rules.yaml` 里写什么就验什么，代码不认表名、不认字段名。

**要做**：
- `config_forge/rules.py`：规则加载 + `Finding` 数据类（`rule_id / level / table / record_id / field / message / value`）
- `config_forge/validator.py`：`Validator(rules).run(tables) -> list[Finding]`
- 实现至少这 8 个 kind：`required / type / range / length / enum / regex / unique / table_unique`
- **`config/rules.yaml` 由你按 `docs/rules.md` 补到 12 条**

**验收（20 条断言）**：12 条规则各至少 1 条正例 1 条反例；用 `data/` 里的错误样本跑出预期的 8 error + 1 warn；**新增一条规则只改 YAML → 断言证明**（在测试里动态写一个临时 rules.yaml）。

**我会挑的地方**：`if table == "activities":` 这种硬编码出现一次就返工。

### C1-2 报告与退出码（2 天）
**目标**：输出人能读、机器也能读。

**要做**：
- 控制台：按 `error` / `warn` 分组，结尾汇总行 `3 张表 / 13 条记录 / error 8 / warn 1`
- `--out report.json`：`{ "summary": {...}, "findings": [...] }`
- 退出码：无 error=0，有 error=1，自身崩溃=2（脚本能靠这个做 CI 门禁）

**验收**：错误文案完全按 `docs/rules.md` 的格式；JSON 能被 `json.load` 解析；退出码三种情况都对。

---

## 6. Sprint 2 · 关系与冲突（5 天）

- **C2-1 外键（2 天）**：`foreign_key` kind，支持 `table.field → other_table.column`；`data/` 里 `RG-03→IT-999`、`ACT-0003→RG-09` 必须被抓到。
- **C2-2 时间重叠（2 天）**：`overlap` kind，只比 `status ∈ {review, live}` 的同 `type` 活动；`ACT-0001` 与 `ACT-0004` 必须报；**复杂度写注释**（排序后 O(n log n) 扫描，不是 O(n²) 两两比——O(n²) 会被打回）。
- **C2-3 策划版报告（1 天）**：`--format md`，输出 `report/validation.md`：一张问题表 + 一句"这 9 个问题里有 8 个必须改，1 个建议确认"。

**验收**：三条都覆盖测试；md 报告不含 Python 栈、不出现英文字段名以外的黑话。

---

## 7. Sprint 3 · AI 生成层（4 天）

- **C3-1 抽象与 Mock（2 天）**：`llm.py` 定义 `class Provider(Protocol): complete(prompt) -> str`；实现 `MockProvider`（按需求文本返回预设 JSON，故意 20% 概率返回坏 JSON）；`HttpProvider` 用 `urllib.request` 打 OpenAI 兼容接口，配置走环境变量 `CF_LLM_BASE_URL / CF_LLM_API_KEY / CF_LLM_MODEL`。**没 key 时自动降级到 Mock 并在日志里喊一声。**
- **C3-2 生成→校验→修复闭环（2 天）**：`generate(requirement) -> rows`，解析失败重试一次（把错误塞回提示词），最多 2 轮；输出"未修复的错误"。
- **提示词要落盘**：`prompts/generate.md`（版本化，改提示词要写原因）。

**验收**：`S-01` 五条样本在 Mock 模式下全流程可跑；HTTP 模式有 key 时能用；任何坏 JSON 都不崩。

---

## 8. Sprint 4 · 度量（这是你简历上的数字）

- **C4-1 扩样本（2 天）**：`samples/requirements.md` 扩到 30 条（含 5 条模糊需求）。
- **C4-2 统计（2 天）**：跑 30 条，输出 `report/metrics.md`：

```
| 指标 | 值 |
|---|---|
| 首次通过率 | 14/30 (47%) |
| 平均修复轮次 | 1.4 |
| 错误分布 | range 31% / foreign_key 24% / enum 18% / required 15% / overlap 12% |
| 拦截率 | 91% 的 AI 错误在校验层被拦下 |
```

**验收**：数字可复现（记模型名 + 日期 + 样本版本）；表下必须有一句结论（"模糊需求里 weight 越界占一半，说明提示词该给区间"）。

---

## 9. Sprint 5 · 引擎闭环（5 天）

- **C5-1 导出（2 天）**：`--export ue-csv`，输出 UE `DataTable` 能导入的 CSV；写 `docs/ue-mapping.md`：Python 类型 → UE 属性类型（`int`→`int32`、`float`→`float`、`datetime`→UE `FDateTime` 的字符串格式坑）。
- **C5-2 引擎内验证（3 天）**：UE5 新建工程，导入 CSV 为 DataTable，写一个蓝图：读第一行 → 打印活动名。截图存 `docs/ue-import.png`。

**验收**：UE 里能看到你的数据，不是"理论上能"。

---

## 10. Sprint 6 · 演示与包装（3 天）

- **C6-1 demo 脚本（1 天）**：`docs/demo.md`，5 分钟、7 步，每步一句话说明"策划看到的是什么"。
- **C6-2 README 重写（1 天）**：给面试官看，不是给自己看。开头三行讲清：谁的问题、怎么解、效果数字。
- **C6-3 简历与问答（1 天）**：三条 bullet + 6 个面试问答（见下）。

---

## 11. 汇报格式（每完成一个 ticket 发一次）

```
ticket：C1-1
跑的命令：python -m pytest -q
结果：20 passed
自我 review：规则分发用 dict 表，加 kind 只需注册；Validator.run 是 O(记录数 × 规则数)，
            1000 行 × 12 规则 ~ 12ms，可接受；丑的地方是 message 格式化塞在 if 里，下次抽出来。
```

---

## 12. 明令禁止（偷懒清单）

1. ❌ `except Exception: pass` 或 `except: return None`
2. ❌ 把校验逻辑写进 `for row in rows:` 的大 if 链里
3. ❌ 用 pandas 读 CSV（这项目的数据量不值得，且掩盖了 CSV 细节）
4. ❌ 硬编码表名/字段名到 `validator.py`
5. ❌ 测试里 `assert True` 凑数，或只测 happy path
6. ❌ 报错文案写英文技术黑话（`KeyError: 'reward_group'`）给策划看
7. ❌ 让 AI 写 `validator.py` 和 `rules.py`（这两个文件必须是你的）

---

## 13. 面试问题库（边做边准备答案）

- 为什么不用现成的 JSON Schema / pydantic？手写引擎的价值在哪？
- 规则多了会不会互相冲突？怎么定优先级？
- 10000 行配置要多久？瓶颈在哪？
- 时间重叠为什么用排序不用两两比？
- LLM 生成的配置错了，责任算谁的？（这是技术策划的必答题）
- 策划说"这个工具不好用"，你怎么判断是真问题还是他不想改流程？
- 你的工具跟 Excel + 数据透视表相比，多解决了什么？
- 配置表格式变了（加字段/改类型），你的工具要改几处？
