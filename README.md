# config-forge · 游戏配置表 AI 生成 + 校验工具

> 目标岗位：**技术策划（Technical Designer）**。这个项目就是"技术策划日常在做的事"的最小可运行版本：
> 策划给一句需求 → 生成配置草稿 → 用规则兜底校验 → 出人能看懂的报错 → 导回引擎。

## 它解决谁的什么问题

策划配活动表时，字段漏填、数值越界、外键写错（引用了一个不存在的奖励组）、两个同类型活动时间重叠——
这些错误在导进引擎前看不出来，进游戏后才发现，改起来要重新走一遍打包流程。

本项目：**用 LLM 出草稿（省时间）+ 用规则引擎兜底（保质量）+ 出人类可读的报告（省沟通）**。
LLM 不追求一次说对，追求"错了能被抓住"。

## 现在能不能跑

还不能。当前只有**契约和任务板**，代码由你按 [TICKETS.md](D:\蓝色大肥鱼\projects\config-forge\TICKETS.md) 逐条实现。

```
config-forge/
  docs/         schema.md  rules.md         ← 数据契约与规则清单（我写，你实现）
  config/       schema.yaml rules.example.yaml ← 声明式配置（你实现解析，并补全 rules.yaml）
  data/         *.csv                       ← 三张表的最小样本（含故意埋的错）
  samples/      requirements.md             ← 自然语言需求样本（Sprint 3 用）
  config_forge/                             ← 你的代码（现在空，只有 __init__.py 占位）
  tests/                                    ← 你的测试
```

## 技术选型（定死，别改）

- Python 3.10+，标准库优先；唯一第三方依赖 `pyyaml`（读配置）+ `pytest`（测试）
- **不引入 pandas / pydantic / jsonschema**：校验器是你要手写的核心，不许被库代劳
- LLM 用 `urllib.request` 直连 OpenAI 兼容接口，零额外依赖；**没有 API key 也必须能跑**（Mock 模式）
- 界面最后再上：先 CLI，Sprint 6 才考虑 Streamlit
