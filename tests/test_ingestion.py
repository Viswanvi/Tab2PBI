import zipfile
from pathlib import Path
from tab2pbi.ingestion import read_tableau_document


def test_twbx_extract(tmp_path: Path):
    p = tmp_path / "sample.twbx"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("Workbook/sample.twb", "<workbook></workbook>")
    doc = read_tableau_document(p)
    assert doc.source_type == "twbx"
    assert "<workbook" in doc.xml_text
