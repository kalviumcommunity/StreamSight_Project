from pathlib import Path
import re

VIEW_PREFIX = "vw_"
AGG_PREFIX = "agg_"

CREATE_VIEW_PATTERN = re.compile(r"^\s*create\s+(or\s+replace\s+)?view\b", re.IGNORECASE)
CREATE_TABLE_PATTERN = re.compile(r"^\s*create\s+(table|table\s+if\s+not\s+exists)\b", re.IGNORECASE)
UPDATED_AT_PATTERN = re.compile(r"updated_at", re.IGNORECASE)


def read_sql_file(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()


def list_sql_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([p for p in path.glob("*.sql") if p.is_file()])


def validate_view_definition(sql: str) -> bool:
    return bool(CREATE_VIEW_PATTERN.search(sql))


def validate_agg_definition(sql: str) -> bool:
    return bool(CREATE_TABLE_PATTERN.search(sql)) and bool(UPDATED_AT_PATTERN.search(sql))


def validate_data_layer(base_dir: str = "database") -> dict:
    base_path = Path(base_dir)
    views_path = base_path / "views"
    aggs_path = base_path / "aggregations"

    report = {
        "views": [],
        "aggregations": [],
        "errors": [],
    }

    for path in list_sql_files(views_path):
        name = path.name
        sql = read_sql_file(path)
        entry = {
            "file": name,
            "valid_name": name.startswith(VIEW_PREFIX),
            "contains_create_view": validate_view_definition(sql),
        }
        if not entry["valid_name"]:
            report["errors"].append(f"View file {name} must start with {VIEW_PREFIX}")
        if not entry["contains_create_view"]:
            report["errors"].append(f"View file {name} must define a CREATE VIEW statement")
        report["views"].append(entry)

    for path in list_sql_files(aggs_path):
        name = path.name
        sql = read_sql_file(path)
        entry = {
            "file": name,
            "valid_name": name.startswith(AGG_PREFIX),
            "contains_create_table": bool(CREATE_TABLE_PATTERN.search(sql)),
            "contains_updated_at": bool(UPDATED_AT_PATTERN.search(sql)),
        }
        if not entry["valid_name"]:
            report["errors"].append(f"Aggregation file {name} must start with {AGG_PREFIX}")
        if not entry["contains_create_table"]:
            report["errors"].append(f"Aggregation file {name} must define a CREATE TABLE statement")
        if not entry["contains_updated_at"]:
            report["errors"].append(f"Aggregation file {name} must include an updated_at column to track freshness")
        report["aggregations"].append(entry)

    return report
