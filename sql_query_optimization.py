import re
from typing import Dict, List

SQL_WHITESPACE = re.compile(r"\s+")
SELECT_STAR_PATTERN = re.compile(r"^\s*select\s+\*\b", re.IGNORECASE)
CTE_PATTERN = re.compile(r"^\s*with\b", re.IGNORECASE)
EARLY_FILTER_SUBQUERY_PATTERN = re.compile(r"from\s*\(\s*select[\s\S]*?where[\s\S]*?\)\s*\w+\s*join", re.IGNORECASE)
EARLY_FILTER_CTE_PATTERN = re.compile(r"with[\s\S]*?as\s*\(\s*select[\s\S]*?where[\s\S]*?\)\s*,?\s*\w+\s*as", re.IGNORECASE)


def normalize_sql(query: str) -> str:
    if not isinstance(query, str):
        raise TypeError("SQL query must be a string")
    normalized = SQL_WHITESPACE.sub(" ", query).strip()
    return normalized


def detect_select_star(query: str) -> bool:
    normalized = normalize_sql(query)
    return bool(SELECT_STAR_PATTERN.search(normalized.lower()))


def detect_cte(query: str) -> bool:
    normalized = normalize_sql(query)
    return bool(CTE_PATTERN.search(normalized))


def detect_early_filtering(query: str) -> bool:
    normalized = normalize_sql(query)
    return bool(EARLY_FILTER_SUBQUERY_PATTERN.search(normalized)) or bool(EARLY_FILTER_CTE_PATTERN.search(normalized))


def detect_filter_after_join(query: str) -> bool:
    normalized = normalize_sql(query).lower()
    has_join = " join " in normalized
    has_where = " where " in normalized
    return has_join and has_where and not detect_early_filtering(query)


def analyze_sql_query(query: str) -> Dict[str, object]:
    if not isinstance(query, str):
        raise TypeError("SQL query must be a string")

    normalized = normalize_sql(query)
    report: Dict[str, object] = {
        "uses_select_star": detect_select_star(normalized),
        "uses_cte": detect_cte(normalized),
        "has_early_filtering": detect_early_filtering(normalized),
        "has_filter_after_join": detect_filter_after_join(normalized),
        "recommendations": [],
    }

    if report["uses_select_star"]:
        report["recommendations"].append(
            "Replace SELECT * with explicit column names to reduce data volume and document query intent."
        )

    if not report["uses_cte"]:
        report["recommendations"].append(
            "Consider using a CTE to structure the query into logical steps for readability and testability."
        )

    if report["has_filter_after_join"]:
        report["recommendations"].append(
            "If possible, filter the driving table before joining to shrink intermediate result sets."
        )

    return report


def suggest_cte_wrapper(query: str, cte_name: str = "filtered_source") -> str:
    normalized = normalize_sql(query)
    if detect_cte(normalized):
        return normalized

    if " from " not in normalized.lower():
        raise ValueError("Unable to wrap query with CTE: FROM clause not found.")

    select_clause, rest = normalized.split(" from ", 1)
    cte = f"WITH {cte_name} AS ({select_clause} FROM {rest})"
    return cte
