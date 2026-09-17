from pathlib import Path
from tab2pbi.assessment import assess
from tab2pbi.parser import parse_tableau


def test_hard_table_calc_is_reviewed():
    assessment = assess(parse_tableau(Path("tests/fixtures/simple.twb")))
    codes = {i.code for i in assessment.review_items}
    assert "calc.table_calc" in codes
    assert "interaction.dashboard_action" in codes
    calc = next(d for d in assessment.dimensions if d.name == "calculations")
    assert calc.review == 1
    assert calc.score == 50
