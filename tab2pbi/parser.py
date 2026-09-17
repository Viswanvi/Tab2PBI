from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .ingestion import read_tableau_document
from .models import DashboardIR, DatasourceIR, FieldIR, MigrationIR, WorksheetIR


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _iter_local(root: ET.Element, name: str):
    for elem in root.iter():
        if _local(elem.tag) == name:
            yield elem


def _children_local(elem: ET.Element, name: str):
    return [child for child in list(elem) if _local(child.tag) == name]


def _calc_formula(column: ET.Element) -> str | None:
    for child in column.iter():
        if _local(child.tag) == "calculation":
            return child.attrib.get("formula")
    return None


def parse_tableau(path: Path) -> MigrationIR:
    doc = read_tableau_document(path)
    try:
        root = ET.fromstring(doc.xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid Tableau XML: {exc}") from exc

    datasources: list[DatasourceIR] = []
    calculation_count = 0
    parameter_count = 0

    for ds in _iter_local(root, "datasource"):
        columns = list(_iter_local(ds, "column"))
        if not columns and not any(_local(c.tag) == "connection" for c in ds.iter()):
            continue
        fields: list[FieldIR] = []
        for col in columns:
            formula = _calc_formula(col)
            if formula:
                calculation_count += 1
            attrs = col.attrib
            name = attrs.get("name") or attrs.get("caption") or "unnamed"
            fields.append(FieldIR(
                name=name,
                caption=attrs.get("caption"),
                datatype=attrs.get("datatype"),
                role=attrs.get("role"),
                field_type=attrs.get("type"),
                formula=formula,
            ))
            if attrs.get("param-domain-type") or "parameter" in (attrs.get("role") or "").lower():
                parameter_count += 1
        connections = sorted({
            c.attrib.get("class")
            for c in _iter_local(ds, "connection")
            if c.attrib.get("class")
        })
        datasources.append(DatasourceIR(
            name=ds.attrib.get("name") or ds.attrib.get("caption") or "datasource",
            caption=ds.attrib.get("caption"),
            connection_classes=connections,
            fields=fields,
        ))

    worksheets: list[WorksheetIR] = []
    worksheet_nodes = []
    for parent in _iter_local(root, "worksheets"):
        worksheet_nodes.extend(_children_local(parent, "worksheet"))
    seen_ws = set()
    for ws in worksheet_nodes:
        name = ws.attrib.get("name") or "Worksheet"
        if name in seen_ws:
            continue
        seen_ws.add(name)
        marks = sorted({m.attrib.get("class", "Automatic") for m in _iter_local(ws, "mark")})
        filters = sum(1 for _ in _iter_local(ws, "filter"))
        xml = ET.tostring(ws, encoding="unicode")
        worksheets.append(WorksheetIR(
            name=name,
            mark_classes=marks,
            filters=filters,
            has_rows_shelf=bool(re.search(r"<rows(?:\s|>)", xml)),
            has_cols_shelf=bool(re.search(r"<cols(?:\s|>)", xml)),
        ))

    dashboards: list[DashboardIR] = []
    dashboard_nodes = []
    for parent in _iter_local(root, "dashboards"):
        dashboard_nodes.extend(_children_local(parent, "dashboard"))
    seen_dash = set()
    for db in dashboard_nodes:
        name = db.attrib.get("name") or "Dashboard"
        if name in seen_dash:
            continue
        seen_dash.add(name)
        dashboards.append(DashboardIR(name=name, zones=sum(1 for _ in _iter_local(db, "zone"))))

    relationships = sum(
        1 for r in _iter_local(root, "relation")
        if (r.attrib.get("type") or "").lower() in {"join", "relationship"}
    )
    actions_parent_count = sum(1 for _ in _iter_local(root, "action"))

    return MigrationIR(
        source_name=doc.name,
        source_type=doc.source_type,
        datasources=datasources,
        worksheets=worksheets,
        dashboards=dashboards,
        parameters=parameter_count,
        relationships=relationships,
        actions=actions_parent_count,
        calculations=calculation_count,
        raw_counts={
            "datasources": len(datasources),
            "fields": sum(len(d.fields) for d in datasources),
            "calculations": calculation_count,
            "worksheets": len(worksheets),
            "dashboards": len(dashboards),
            "parameters": parameter_count,
            "relationships": relationships,
            "actions": actions_parent_count,
        },
    )
