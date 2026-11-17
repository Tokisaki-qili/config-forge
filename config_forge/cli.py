import argparse
import sys
from pathlib import Path

from config_forge.loader import SchemaError, load_schema, load_table


if __name__ == "__main__":
    sys.exit(main())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog = "config_forge"
        description = "读取配置表，输出统计数据"
    )
    parser.add_argument("--schema", required=True, type=Path, help="schema.yaml的路径 例如：config/schema.yaml")
    parser.add_argument("--data", default=Path("data"), type=Path, help="数据表所在目录，默认 data")
    parser.add_argument("--out", default=Path("out"), type=Path, help="输出目录，默认 out")
    return parser


def main(argv:list[str] |None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")





