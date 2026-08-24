"""
Core analytics engine for StreamSight.

All business-metric calculations live here so route handlers stay thin.
Uses pandas/numpy for aggregation once raw rows are pulled from the DB.
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.extensions import db
from app.models import Engagement, Video, Category, WatchSession, Bookmark, SearchActivity
from app.utils.helpers import safe_div
from app.services.retention_service import calculate_retention_score, classify_acquisition_recommendation

DROPOFF_BUCKETS = [
    (0, 25, "0-25%"),
    (25, 50, "25-50%"),
    (50, 75, "50-75%"),
    (75, 90, "75-90%"),
    (90, 100.0001, "90-100%"),
]

TRENDING_WEIGHTS = {
    "views": 0.40,
    "completion": 0.30,
    "watch_time": 0.15,
    "replay": 0.15,
}


def _empty_dataframe():
    return pd.DataFrame(
        columns=[
            "video_id", "video_title", "category_id", "category_name",
            "user_id", "watch_duration", "completion_rate", "pause_count",
            "replay_count", "seek_count", "session_duration", "video_duration",
            "created_at",
        ]
    )


def engagement_dataframe(date_from=None, date_to=None, category_id=None, video_id=None):
    query = (
        db.session.query(
            Engagement.video_id,
            Video.title.label("video_title"),
            Video.category_id,
            Category.name.label("category_name"),
            Engagement.user_id,
            Engagement.watch_duration,
            Engagement.completion_rate,
            Engagement.pause_count,
            Engagement.replay_count,
            Engagement.seek_count,
            WatchSession.session_duration,
            Video.duration.label("video_duration"),
            Engagement.created_at,
        )
        .join(Video, Engagement.video_id == Video.id)
        .join(Category, Video.category_id == Category.id)
        .outerjoin(WatchSession, Engagement.session_id == WatchSession.id)
    )

    if date_from:
        query = query.filter(Engagement.created_at >= date_from)
    if date_to:
        query = query.filter(Engagement.created_at <= date_to)
    if category_id:
        query = query.filter(Video.category_id == category_id)
    if video_id:
        query = query.filter(Engagement.video_id == video_id)

    rows = query.all()
    if not rows:
        return _empty_dataframe()

    df = pd.DataFrame(rows, columns=[
        "video_id", "video_title", "category_id", "category_name", "user_id",
        "watch_duration", "completion_rate", "pause_count", "replay_count",
        "seek_count", "session_duration", "video_duration", "created_at",
    ])
    df["session_duration"] = df["session_duration"].fillna(0)
    return df


def summary_metrics(date_from=None, date_to=None, category_id=None, video_id=None):
    df = engagement_dataframe(date_from, date_to, category_id, video_id)
    total_views = len(df)
    if total_views == 0:
        return {
            "total_views": 0,
            "average_watch_time": 0,
            "average_completion_rate": 0,
            "average_pause_frequency": 0,
        }

    total_watch_duration = float(df["watch_duration"].sum())
    return {
        "total_views": int(total_views),
        "average_watch_time": round(safe_div(total_watch_duration, total_views), 2),
        "average_completion_rate": round(float(df["completion_rate"].mean()), 2),
        "average_pause_frequency": round(safe_div(float(df["pause_count"].sum()), total_views), 2),
    }


def _video_retention_score(group):
    avg_watch_duration = float(group["watch_duration"].mean())
    avg_video_duration = float(group["video_duration"].iloc[0]) if len(group) else 0
    avg_completion_rate = float(group["completion_rate"].mean())
    avg_session_duration = float(group["session_duration"].mean())
    unique_viewers = group["user_id"].nunique()
    repeat_view_count = safe_div(float(group["replay_count"].sum()), unique_viewers)

    return calculate_retention_score(
        avg_watch_duration, avg_video_duration, avg_completion_rate,
        avg_session_duration, repeat_view_count,
    )


def content_performance(date_from=None, date_to=None, category_id=None, video_id=None):
    df = engagement_dataframe(date_from, date_to, category_id, video_id)
    if df.empty:
        return []

    bookmark_counts = dict(
        db.session.query(Bookmark.video_id, db.func.count(Bookmark.id))
        .group_by(Bookmark.video_id)
        .all()
    )

    results = []
    for vid, group in df.groupby("video_id"):
        views = len(group)
        unique_viewers = int(group["user_id"].nunique())
        replay_rate = round(safe_div(float((group["replay_count"] > 0).sum()), views) * 100, 2)

        results.append({
            "video_id": int(vid),
            "title": str(group["video_title"].iloc[0]),
            "category": str(group["category_name"].iloc[0]),
            "total_views": views,
            "unique_viewers": unique_viewers,
            "average_watch_duration": round(float(group["watch_duration"].mean()), 2),
            "average_completion_rate": round(float(group["completion_rate"].mean()), 2),
            "average_pause_count": round(float(group["pause_count"].mean()), 2),
            "replay_rate": replay_rate,
            "bookmark_count": int(bookmark_counts.get(int(vid), 0)),
            "average_retention_score": _video_retention_score(group),
        })

    results.sort(key=lambda r: r["average_retention_score"], reverse=True)
    return results


def dropoff_analysis(date_from=None, date_to=None, category_id=None, video_id=None):
    df = engagement_dataframe(date_from, date_to, category_id, video_id)
    if df.empty:
        return [{"range": label, "viewers": 0, "percentage": 0.0} for _, _, label in DROPOFF_BUCKETS]

    total = len(df)
    conditions = [
        (df["completion_rate"] >= low) & (df["completion_rate"] < high)
        for low, high, _ in DROPOFF_BUCKETS
    ]
    labels = [label for _, _, label in DROPOFF_BUCKETS]
    df["bucket"] = np.select(conditions, labels, default=labels[-1])

    counts = df["bucket"].value_counts().to_dict()
    result = []
    for label in labels:
        viewers = int(counts.get(label, 0))
        result.append({
            "range": label,
            "viewers": viewers,
            "percentage": round(safe_div(viewers, total) * 100, 2),
        })
    return result


def trending_content(period="weekly", limit=10):
    now = datetime.utcnow()
    if period == "daily":
        since = now - timedelta(days=1)
    elif period == "monthly":
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=7)

    df = engagement_dataframe(date_from=since, date_to=now)
    if df.empty:
        return []

    thumbnails = dict(
        db.session.query(Video.id, Video.thumbnail_url).filter(Video.id.in_(df["video_id"].unique().tolist()))
    )

    rows = []
    max_views = df.groupby("video_id").size().max() or 1
    for vid, group in df.groupby("video_id"):
        views = len(group)
        video_duration = float(group["video_duration"].iloc[0])
        avg_completion = float(group["completion_rate"].mean())
        avg_watch_time_ratio = safe_div(float(group["watch_duration"].mean()), video_duration or 1)
        replay_ratio = safe_div(float((group["replay_count"] > 0).sum()), views)

        score = (
            safe_div(views, max_views) * 100 * TRENDING_WEIGHTS["views"]
            + avg_completion * TRENDING_WEIGHTS["completion"]
            + min(avg_watch_time_ratio, 1) * 100 * TRENDING_WEIGHTS["watch_time"]
            + replay_ratio * 100 * TRENDING_WEIGHTS["replay"]
        )

        rows.append({
            "video_id": int(vid),
            "title": str(group["video_title"].iloc[0]),
            "category": str(group["category_name"].iloc[0]),
            "duration": int(video_duration),
            "thumbnail_url": thumbnails.get(int(vid)),
            "views": views,
            "average_completion_rate": round(avg_completion, 2),
            "retention_score": _video_retention_score(group),
            "trending_score": round(score, 2),
        })

    rows.sort(key=lambda r: r["trending_score"], reverse=True)
    for idx, row in enumerate(rows[:limit], start=1):
        row["rank"] = idx
    return rows[:limit]


def category_analytics(date_from=None, date_to=None):
    df = engagement_dataframe(date_from, date_to)
    categories = {c.id: c.name for c in Category.query.all()}
    if df.empty:
        return [
            {"category_id": cid, "category": name, "views": 0, "average_watch_duration": 0,
             "average_completion_rate": 0, "average_pause_frequency": 0,
             "retention_score": 0, "unique_viewers": 0}
            for cid, name in categories.items()
        ]

    results = []
    for cid, group in df.groupby("category_id"):
        views = len(group)
        results.append({
            "category_id": int(cid),
            "category": str(group["category_name"].iloc[0]),
            "views": views,
            "average_watch_duration": round(float(group["watch_duration"].mean()), 2),
            "average_completion_rate": round(float(group["completion_rate"].mean()), 2),
            "average_pause_frequency": round(safe_div(float(group["pause_count"].sum()), views), 2),
            "retention_score": _video_retention_score(group),
            "unique_viewers": int(group["user_id"].nunique()),
        })
    results.sort(key=lambda r: r["views"], reverse=True)
    return results


def search_analytics(limit=10):
    rows = SearchActivity.query.all()
    if not rows:
        return {"top_keywords": [], "top_categories": []}

    df = pd.DataFrame([{"query": r.search_query.lower().strip(), "category": r.category} for r in rows])

    top_keywords = (
        df["query"].value_counts().head(limit).reset_index().values.tolist()
    )
    top_categories = (
        df[df["category"].notna()]["category"].value_counts().head(limit).reset_index().values.tolist()
    )

    return {
        "top_keywords": [{"query": q, "count": int(c)} for q, c in top_keywords],
        "top_categories": [{"category": cat, "count": int(c)} for cat, c in top_categories],
    }


def search_trends(period="daily"):
    rows = SearchActivity.query.all()
    if not rows:
        return {"trend": [], "no_result_searches": []}

    df = pd.DataFrame([
        {"timestamp": r.timestamp, "query": r.search_query, "result_count": r.result_count}
        for r in rows
    ])
    freq = {"daily": "D", "weekly": "W", "monthly": "M"}.get(period, "D")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    trend = (
        df.set_index("timestamp").resample(freq).size().reset_index(name="count")
    )
    trend["timestamp"] = trend["timestamp"].dt.strftime("%Y-%m-%d")

    no_results = df[df["result_count"] == 0]["query"].value_counts().head(20).reset_index().values.tolist()

    return {
        "trend": trend.to_dict(orient="records"),
        "no_result_searches": [{"query": q, "count": int(c)} for q, c in no_results],
    }


def engagement_trends(period="daily", date_from=None, date_to=None):
    df = engagement_dataframe(date_from, date_to)
    if df.empty:
        return []

    freq = {"daily": "D", "weekly": "W", "monthly": "M"}.get(period, "D")
    df["created_at"] = pd.to_datetime(df["created_at"])
    df = df.set_index("created_at")

    grouped = df.resample(freq).agg(
        views=("video_id", "count"),
        average_watch_time=("watch_duration", "mean"),
        average_completion_rate=("completion_rate", "mean"),
        average_pause_frequency=("pause_count", "mean"),
    ).fillna(0).reset_index()

    grouped["created_at"] = grouped["created_at"].dt.strftime("%Y-%m-%d")
    grouped = grouped.round(2)

    # retention score per period requires a groupby pass, computed separately
    scores = []
    for period_start, group in df.resample(freq):
        if len(group) == 0:
            scores.append(0)
        else:
            scores.append(_video_retention_score(group))
    grouped["retention_score"] = scores

    return grouped.to_dict(orient="records")


def acquisition_insights(date_from=None, date_to=None):
    performance = content_performance(date_from, date_to)
    dropoff_by_video = {}
    for row in performance:
        buckets = dropoff_analysis(date_from, date_to, video_id=row["video_id"])
        early = sum(b["percentage"] for b in buckets if b["range"] in ("0-25%", "25-50%"))
        dropoff_by_video[row["video_id"]] = early

    strong, needs_investigation, hidden = [], [], []

    for row in performance:
        metrics = {
            "completion_rate": row["average_completion_rate"],
            "pause_frequency": row["average_pause_count"],
            "retention_score": row["average_retention_score"],
            "repeat_view_ratio": safe_div(row["replay_rate"], 100),
            "views": row["total_views"],
            "dropoff_early_pct": dropoff_by_video.get(row["video_id"], 0),
        }
        classification = classify_acquisition_recommendation(metrics)
        if not classification:
            continue
        label, reason = classification
        entry = {
            "video": row["title"],
            "video_id": row["video_id"],
            "category": row["category"],
            "views": row["total_views"],
            "completion_rate": row["average_completion_rate"],
            "pause_frequency": row["average_pause_count"],
            "retention_score": row["average_retention_score"],
            "recommendation": label,
            "reason": reason,
        }
        if label == "Strong Acquisition Candidate":
            strong.append(entry)
        elif label == "Needs Investigation":
            needs_investigation.append(entry)
        else:
            hidden.append(entry)

    strong.sort(key=lambda r: r["retention_score"], reverse=True)
    hidden.sort(key=lambda r: r["retention_score"], reverse=True)
    needs_investigation.sort(key=lambda r: r["completion_rate"])

    return {
        "strong_acquisition_candidates": strong,
        "needs_investigation": needs_investigation,
        "hidden_performers": hidden,
    }


def acquisition_summary(date_from=None, date_to=None):
    insights = acquisition_insights(date_from, date_to)
    categories = category_analytics(date_from, date_to)
    dropoff = dropoff_analysis(date_from, date_to)

    top_content = insights["strong_acquisition_candidates"][:3] + insights["hidden_performers"][:2]
    weak_categories = sorted(categories, key=lambda c: c["retention_score"])[:2]
    strong_categories = sorted(categories, key=lambda c: c["retention_score"], reverse=True)[:2]
    dominant_dropoff = max(dropoff, key=lambda b: b["percentage"]) if dropoff else None

    return {
        "top_content_to_invest_in": [
            {"title": c["video"], "reason": c["reason"]} for c in top_content
        ],
        "content_needing_investigation": [
            {"title": c["video"], "reason": c["reason"]}
            for c in insights["needs_investigation"][:3]
        ],
        "high_potential_categories": [c["category"] for c in strong_categories],
        "weak_categories": [c["category"] for c in weak_categories],
        "dominant_dropoff_stage": dominant_dropoff["range"] if dominant_dropoff else None,
    }


def dashboard_overview():
    from app.models import User, Video

    now = datetime.utcnow()
    since = now - timedelta(days=30)

    metrics = summary_metrics(date_from=since, date_to=now)
    performance = content_performance(date_from=since, date_to=now)
    trending = trending_content(period="weekly", limit=5)
    categories = category_analytics(date_from=since, date_to=now)
    dropoff = dropoff_analysis(date_from=since, date_to=now)
    trends = engagement_trends(period="daily", date_from=now - timedelta(days=7), date_to=now)

    return {
        "total_users": User.query.count(),
        "total_videos": Video.query.filter_by(is_active=True).count(),
        "total_views": metrics["total_views"],
        "average_watch_time": metrics["average_watch_time"],
        "average_completion_rate": metrics["average_completion_rate"],
        "average_pause_frequency": metrics["average_pause_frequency"],
        "retention_score": (
            round(sum(p["average_retention_score"] for p in performance) / len(performance), 2)
            if performance else 0
        ),
        "top_performing_videos": performance[:5],
        "trending_videos": trending,
        "category_performance": categories,
        "dropoff_distribution": dropoff,
        "recent_engagement_trends": trends,
    }
