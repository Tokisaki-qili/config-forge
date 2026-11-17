from dataclasses import dataclass, field
from pathlib import Path

import yaml
import csv


class SchemaError(Exception):
    """配置契约错误：schema 结构不对，或 CSV 表头和 schema 对不上。"""


@dataclass
class ParseError:
    file: str        # "activities.csv"
    line_no: int     # 文件里的真实行号：1 = 表头，2 = 第一条数据
    column: str      # 字段名，比如 "weight"
    raw_value: str   # 原始值，比如 "1.5x"（是字符串，不是数字）
    message: str     # 人话说明，比如 "不是合法小数"
    level: str = "error"   # 多余列是 warn

    def __str__(self) -> str:
        return f"{self.file} 第 {self.line_no} 行：{self.column}=「{self.raw_value}」{self.message}"


@dataclass
class LoadResult:
    table: str = ""
    records: list[dict] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        """返回表格的行数（不含表头）"""
        return len(self.records)


#`load_schema(path) -> dict`：读 `config/schema.yaml`，校验 `version` 存在、每张表有 `file` 和 `columns`
def load_schema(path) -> dict:
    with open(path, "r", encoding="utf-8-sig") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise SchemaError(f"schema 文件 {path} 不是字典，实际是 {type(data).__name__}")

    if "tables" not in data:
        raise SchemaError("schema 缺少 tables 字段")

    if not isinstance(data["tables"], dict):
        raise SchemaError(f"schema 的 tables 必须是字典，实际是 {type(data['tables']).__name__}")

    if "version" not in data:
        raise SchemaError("schema 缺少 version 字段")

    for name, spec in data["tables"].items():
        if not isinstance(spec, dict):
            raise SchemaError(f"表 {name} 的配置必须是字典，实际是 {type(spec).__name__}")

        file = spec.get("file")
        columns = spec.get("columns")
        if not file:
            raise SchemaError(f"表 {name} 的配置缺少 file 字段")
        if not columns:
            raise SchemaError(f"表 {name} 的配置缺少 columns 字段")
        if not isinstance(columns, dict):
            raise SchemaError(f"表 {name} 的 columns 必须是字典，实际是 {type(columns).__name__}")

    return data


def load_table(name, spec, data_dir) -> LoadResult:
    result = LoadResult(table=name)
    path = data_dir / Path(spec["file"]).name

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)

        header = next(reader, None)
        header = [h.strip() for h in header] if header else []

        if header and len(header) != len(set(header)):
            result.errors.append(ParseError(file=path.name, line_no=1, column="", raw_value="", level="warning", message="表头有重复列名，同名列只会保留最后一个"))


        expected = set(spec["columns"].keys())
        actual = set(header or [])
        missing = expected - actual
        extra = actual - expected

        if missing:
            msg = f"{path.name} 缺少列 {sorted(missing)}"
            if extra:
                msg += f"，多出列 {sorted(extra)}（可能是拼写错误）"
            raise SchemaError(msg)

        if extra:
            result.errors.append(ParseError(
                file=path.name,
                line_no=1,
                column=",".join(sorted(extra)),
                raw_value=",".join(sorted(extra)),
                message=f"表头多出未定义的列，这些列不会被校验",
                level="warning",
            ))

        for line_no, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(header):
                result.errors.append(ParseError(file=path.name, line_no=line_no, column="", raw_value="", message=f"列数不匹配，表头 {len(header)} 列，实际 {len(row)} 列"))
                continue
            record = dict(zip(header, row))
            result.records.append(record)

    return result
