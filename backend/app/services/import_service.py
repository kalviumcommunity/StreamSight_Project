"""
Dataset import pipeline for bulk-loading engagement data (CSV/JSON/Excel).
Profiles, validates, and reports on the incoming data before writing valid
rows to the database.
"""
import pandas as pd

from app.extensions import db
from app.models import Engagement, User, Video
from app.utils.errors import ValidationError

REQUIRED_COLUMNS = ["user_id", "video_id", "watch_duration", "completion_rate"]
OPTIONAL_COLUMNS = ["pause_count", "replay_count", "seek_count"]


def _load_dataframe(file_storage):
    filename = (file_storage.filename or "").lower()
    if filename.endswith(".csv"):
        return pd.read_csv(file_storage)
    if filename.endswith(".json"):
        return pd.read_json(file_storage)
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(file_storage)
    raise ValidationError("Unsupported file type. Use CSV, JSON, or Excel (.xlsx)")


def import_engagement_data(file_storage):
    df = _load_dataframe(file_storage)

    report = {
        "total_records": int(len(df)),
        "valid_records": 0,
        "invalid_records": 0,
        "missing_values": {},
        "duplicates": 0,
        "validation_failures": [],
    }

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")

    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = 0

    missing_counts = df[REQUIRED_COLUMNS].isnull().sum()
    report["missing_values"] = {k: int(v) for k, v in missing_counts.items() if v > 0}

    before = len(df)
    df = df.drop_duplicates()
    report["duplicates"] = int(before - len(df))

    valid_user_ids = {u.id for u in User.query.with_entities(User.id).all()}
    valid_video_ids = {v.id for v in Video.query.with_entities(Video.id).all()}

    valid_rows = []
    for idx, row in df.iterrows():
        errors = []
        if pd.isnull(row.get("user_id")) or int(row["user_id"]) not in valid_user_ids:
            errors.append("unknown or missing user_id")
        if pd.isnull(row.get("video_id")) or int(row["video_id"]) not in valid_video_ids:
            errors.append("unknown or missing video_id")

        watch_duration = row.get("watch_duration")
        if pd.isnull(watch_duration) or float(watch_duration) < 0:
            errors.append("watch_duration must be a non-negative number")

        completion_rate = row.get("completion_rate")
        if pd.isnull(completion_rate) or not (0 <= float(completion_rate) <= 100):
            errors.append("completion_rate must be between 0 and 100")

        pause_count = row.get("pause_count", 0)
        if pd.notnull(pause_count) and float(pause_count) < 0:
            errors.append("pause_count cannot be negative")

        if errors:
            report["validation_failures"].append({"row": int(idx), "errors": errors})
            continue

        valid_rows.append(row)

    report["valid_records"] = len(valid_rows)
    report["invalid_records"] = report["total_records"] - report["valid_records"]

    for row in valid_rows:
        engagement = Engagement(
            user_id=int(row["user_id"]),
            video_id=int(row["video_id"]),
            watch_duration=int(row["watch_duration"]),
            completion_rate=float(row["completion_rate"]),
            pause_count=int(row.get("pause_count", 0) or 0),
            replay_count=int(row.get("replay_count", 0) or 0),
            seek_count=int(row.get("seek_count", 0) or 0),
        )
        db.session.add(engagement)

    db.session.commit()

    return report
