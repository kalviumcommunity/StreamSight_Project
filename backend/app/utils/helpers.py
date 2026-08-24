def paginate_query(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": pagination.items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def parse_date_range(args):
    from datetime import datetime, timedelta

    date_from = args.get("date_from")
    date_to = args.get("date_to")

    end = datetime.utcnow()
    if date_to:
        end = datetime.fromisoformat(date_to)

    if date_from:
        start = datetime.fromisoformat(date_from)
    else:
        start = end - timedelta(days=30)

    return start, end


def safe_div(numerator, denominator, default=0.0):
    if not denominator:
        return default
    return numerator / denominator
