"""config-forge：游戏配置表 AI 生成 + 校验工具。

模块规划（你来实现，不要提前建空文件）：
    loader.py    读 schema.yaml 与三张 CSV，产出记录 + 解析错误
    model.py     数据类与类型转换（只管类型，不管业务）
    rules.py     规则加载与 Finding 定义
    validator.py 校验引擎（规则驱动，禁止硬编码表名）
    report.py    控制台 / JSON / Markdown 三种输出
    llm.py       Provider 抽象 + MockProvider + HttpProvider
    cli.py       命令行入口
"""

__version__ = "0.1.0"
