import argparse
import sys
from pathlib import Path

import yaml

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


def _configure_utf8(stream) -> None:
    """尽量把控制台输出切到 UTF-8，避免 Windows 默认 GBK 把中文打成乱码。

    stdout / stderr 可能被重定向成管道、IDE 或测试框架的包装对象，
    它们不一定支持 reconfigure（或者只支持部分参数），所以失败时保持原样，
    不能让编码设置把整个命令拖崩。
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        return
    try:
        reconfigure(encoding="utf-8")
    except (AttributeError, TypeError, ValueError):
        # io.UnsupportedOperation 是 ValueError 的子类
        pass


def main(argv: list[str] | None = None) -> int:
    _configure_utf8(sys.stdout)
    _configure_utf8(sys.stderr)

    args = build_parser().parse_args(argv)

    try:
        contract = load_schema(args.schema)
    except FileNotFoundError:
        print(f"schema 文件不存在：{args.schema}", file=sys.stderr)
        return 2
    except yaml.YAMLError as exc:
        print(f"schema 不是合法的 YAML：{exc}", file=sys.stderr)
        return 2
    except (SchemaError, OSError, UnicodeError) as exc:
        print(f"读取 schema 失败：{exc}", file=sys.stderr)
        return 2

    print(f"schema: {args.schema} (version {contract.get('version')}, tables: {len(contract['tables'])} 张表)")

    total_rows = total_errors = total_warnings = 0

    for name, spec in contract["tables"].items():
        try:
            result = load_table(name, spec, args.data)
        except FileNotFoundError as exc:
            print(f"表 {name} 的数据文件找不到：{exc.filename}", file=sys.stderr)
            return 2
        except SchemaError as exc:
            # 缺列属于配置契约错误：schema 和 CSV 表头对不上
            print(f"表 {name} 与 CSV 表头不一致：{exc}", file=sys.stderr)
            return 2
        except (OSError, UnicodeError) as exc:
            print(f"读取表 {name} 的数据文件失败：{exc}", file=sys.stderr)
            return 2

        errs = sum(1 for e in result.errors if e.level == "error")
        warns = len(result.errors) - errs
        total_rows += result.row_count
        total_errors += errs
        total_warnings += warns
        print(f"{name:<15} {result.row_count} 行 {errs} 错 {warns} 警告")

    print(f"合计：{total_rows}行 {total_errors}错误 {total_warnings}警告")

    # 有 error 时返回 1，方便 CI / 脚本把它当门禁；没有 error 才是 0
    return 1 if total_errors else 0

if __name__ == "__main__":
    sys.exit(main())




