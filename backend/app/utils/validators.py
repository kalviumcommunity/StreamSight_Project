import re
from app.utils.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_fields(data, fields):
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")


def validate_email(email):
    if not email or not EMAIL_RE.match(email):
        raise ValidationError("Invalid email address")
    return email.strip().lower()


def validate_password(password):
    if not password or len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long")
    return password


def validate_non_negative(value, field_name):
    if value is None:
        return 0
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number")
    if value < 0:
        raise ValidationError(f"{field_name} cannot be negative")
    return value


def validate_completion_rate(value):
    value = validate_non_negative(value, "completion_rate")
    if value > 100:
        raise ValidationError("completion_rate must be between 0 and 100")
    return value


def validate_positive(value, field_name):
    value = validate_non_negative(value, field_name)
    if value <= 0:
        raise ValidationError(f"{field_name} must be greater than 0")
    return value


def validate_pagination(args):
    try:
        page = max(1, int(args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(args.get("per_page", 20))
    except (TypeError, ValueError):
        per_page = 20
    per_page = min(max(per_page, 1), 100)
    return page, per_page
