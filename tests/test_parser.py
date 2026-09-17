from pathlib import Path
from tab2pbi.parser import parse_tableau


def test_parse_simple_workbook():
    ir = parse_tableau(Path("tests/fixtures/simple.twb"))
    assert ir.source_type == "twb"
    assert ir.raw_counts["datasources"] == 1
    assert ir.raw_counts["calculations"] == 2
    assert ir.raw_counts["worksheets"] == 1
    assert ir.raw_counts["dashboards"] == 1
    assert ir.actions == 1
    assert ir.worksheets[0].mark_classes == ["Bar"]
