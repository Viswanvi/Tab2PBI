from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {".twb", ".twbx", ".tds", ".tdsx"}


class UnsupportedInput(ValueError):
    pass


@dataclass(frozen=True)
class TableauDocument:
    name: str
    source_type: str
    xml_text: str


def _inner_xml(data: bytes, expected_suffix: str) -> str:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        candidates = [n for n in zf.namelist() if n.lower().endswith(expected_suffix)]
        if not candidates:
            raise UnsupportedInput(f"Archive does not contain {expected_suffix}")
        candidates.sort(key=lambda n: (n.count("/"), len(n), n.lower()))
        return zf.read(candidates[0]).decode("utf-8-sig")


def read_tableau_document(path: Path) -> TableauDocument:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise UnsupportedInput(f"Unsupported Tableau asset: {suffix or '<no extension>'}")
    data = path.read_bytes()
    if suffix == ".twbx":
        text = _inner_xml(data, ".twb")
    elif suffix == ".tdsx":
        text = _inner_xml(data, ".tds")
    else:
        text = data.decode("utf-8-sig")
    return TableauDocument(name=path.stem, source_type=suffix[1:], xml_text=text)
