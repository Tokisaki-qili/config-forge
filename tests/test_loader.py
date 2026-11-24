from pathlib import Path

import pytest

from config_forge.loader import SchemaError, load_schema, load_table

# tests/test_loader.py 在项目根目录的下一层，所以 parent.parent 就是项目根
ROOT = Path(__file__).resolve().parent.parent


def test_real_tables():
    """真数据：三张表 5/5/3 行，且没有任何解析问题。"""
    contract = load_schema(ROOT / "config" / "schema.yaml")
    counts = {}
    for name, spec in contract["tables"].items():
        result = load_table(name, spec, ROOT / "data")
        counts[name] = result.row_count
        assert result.errors == []
    assert counts == {"activities": 5, "reward_groups": 5, "items": 3}


def test_empty_schema_raises(tmp_path):
    """0 字节的 schema 应该是契约错误，不是返回 None。"""
    p = tmp_path / "schema.yaml"
    p.write_text("", encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(p)


def test_missing_column_raises(tmp_path):
    """CSV 少一列 → 致命错误。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\ntables:\n  t:\n    file: t.csv\n    columns:\n      a: {type: string}\n",
        encoding="utf-8",
    )
    (tmp_path / "t.csv").write_text("b\n1\n", encoding="utf-8")
    contract = load_schema(tmp_path / "schema.yaml")
    with pytest.raises(SchemaError):
        load_table("t", contract["tables"]["t"], tmp_path)


def test_extra_column_is_warning(tmp_path):
    """CSV 多一列 → 只警告，不致命。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\ntables:\n  t:\n    file: t.csv\n    columns:\n      a: {type: string}\n",
        encoding="utf-8",
    )
    (tmp_path / "t.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    contract = load_schema(tmp_path / "schema.yaml")
    result = load_table("t", contract["tables"]["t"], tmp_path)
    assert len(result.errors) == 1
    assert result.errors[0].level == "warning"
    assert result.row_count == 1

def test_missing_version_raises(tmp_path):
    """schema 缺 version 字段 → 契约错误。"""
    (tmp_path / "schema.yaml").write_text(
        "tables:\n  t:\n    file: t.csv\n    columns:\n      a: {type: string}\n",
        encoding="utf-8",
    )
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "schema.yaml")


def test_missing_tables_raises(tmp_path):
    """schema 缺 tables 字段 → 契约错误。"""
    (tmp_path / "schema.yaml").write_text("version: 1\n", encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "schema.yaml")


def test_tables_not_mapping_raises(tmp_path):
    """tables 写成列表 → 契约错误（不是 AttributeError）。"""
    (tmp_path / "schema.yaml").write_text("version: 1\ntables: [1, 2]\n", encoding="utf-8")
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "schema.yaml")


def test_table_missing_file_raises(tmp_path):
    """某张表没写 file → 契约错误。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\ntables:\n  t:\n    columns:\n      a: {type: string}\n",
        encoding="utf-8",
    )
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "schema.yaml")


def test_table_missing_columns_raises(tmp_path):
    """某张表没写 columns → 契约错误。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\ntables:\n  t:\n    file: t.csv\n",
        encoding="utf-8",
    )
    with pytest.raises(SchemaError):
        load_schema(tmp_path / "schema.yaml")


def test_row_column_count_mismatch_is_error(tmp_path):
    """某行比表头少一个值 → 1 条 error，且这一行不进 records。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\n"
        "tables:\n"
        "  t:\n"
        "    file: t.csv\n"
        "    columns:\n"
        "      a: {type: string}\n"
        "      b: {type: string}\n",
        encoding="utf-8",
    )
    (tmp_path / "t.csv").write_text("a,b\n1\n", encoding="utf-8")
    contract = load_schema(tmp_path / "schema.yaml")
    result = load_table("t", contract["tables"]["t"], tmp_path)
    assert len(result.errors) == 1
    assert result.errors[0].level == "error"
    assert result.row_count == 0


def test_blank_line_at_end_is_ignored(tmp_path):
    """文件末尾多一个空行 → 不产生假的空记录。"""
    (tmp_path / "schema.yaml").write_text(
        "version: 1\n"
        "tables:\n"
        "  t:\n"
        "    file: t.csv\n"
        "    columns:\n"
        "      a: {type: string}\n"
        "      b: {type: string}\n",
        encoding="utf-8",
    )
    (tmp_path / "t.csv").write_text("a,b\n1,2\n\n", encoding="utf-8")
    contract = load_schema(tmp_path / "schema.yaml")
    result = load_table("t", contract["tables"]["t"], tmp_path)
    assert result.row_count == 1
    assert result.errors == []
