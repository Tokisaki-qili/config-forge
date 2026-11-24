import argparse
import sys
from pathlib import Path

from config_forge.loader import SchemaError, load_schema, load_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="config_forge",
        description="读取配置表，输出统计数据"
    )
    parser.add_argument("--schema", required=True, type=Path, help="schema.yaml的路径 例如：config/schema.yaml")
    parser.add_argument("--data", default=Path("data"), type=Path, help="数据表所在目录，默认 data")
    parser.add_argument("--out", default=Path("out"), type=Path, help="输出目录，默认 out")
    return parser


def main(argv:list[str] |None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    args = build_parser().parse_args(argv)
    try:
        contract = load_schema(args.schema)
    except (SchemaError, FileNotFoundError) as exc:
        print(f"读取schema失败：{exc}", file=sys.stderr)
        return 2

    print(f"schema: {args.schema} (version {contract.get('version')}, tables: {len(contract['tables'])} 张表)")

    total_rows = total_errors = total_warnings = 0

    for name, spec in contract["tables"].items():
        try:
            result = load_table(name, spec, args.data)
        except FileNotFoundError as exc:
            print(f"表 {name} 的数据文件找不到：{exc.filename}", file=sys.stderr)
            return 2
        errs = sum(1 for e in result.errors if e.level == "error")
        warns = len(result.errors) - errs
        total_rows += result.row_count
        total_errors += errs
        total_warnings += warns
        print(f"{name:<15} {result.row_count} 行 {errs} 错 {warns} 警告")

    print(f"合计：{total_rows}行 {total_errors}错误 {total_warnings}警告")

    return 0

if __name__ == "__main__":
    sys.exit(main())



