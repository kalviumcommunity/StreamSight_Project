from datetime import datetime, timedelta

from app.extensions import db
from app.models import Video, WatchHistory, Bookmark
from app.services.analytics_service import trending_content


def continue_watching(user_id, limit=10):
    rows = (
        WatchHistory.query.filter(
            WatchHistory.user_id == user_id,
            WatchHistory.completion_rate > 0,
            WatchHistory.completion_rate < 90,
        )
        .order_by(WatchHistory.watched_at.desc())
        .limit(limit)
        .all()
    )
    seen = set()
    result = []
    for row in rows:
        if row.video_id in seen:
            continue
        seen.add(row.video_id)
        result.append(row.to_dict())
    return result


def recommended_for_user(user_id, limit=10):
    """
    Recommend content from categories the user has previously engaged with,
    ranked by trending score, excluding videos already completed.
    """
    watched_video_ids = {
        row.video_id
        for row in WatchHistory.query.filter_by(user_id=user_id, completed=True).all()
    }
    liked_category_ids = {
        row.video.category_id
        for row in WatchHistory.query.filter_by(user_id=user_id).all()
        if row.video
    }

    trending = trending_content(period="monthly", limit=50)
    candidates = [
        row for row in trending
        if row["video_id"] not in watched_video_ids
    ]

    if liked_category_ids:
        candidates.sort(
            key=lambda r: (r["category"] not in liked_category_ids, -r["trending_score"])
        )
    else:
        candidates.sort(key=lambda r: -r["trending_score"])

    return candidates[:limit]


def featured_content():
    video = (
        Video.query.filter_by(is_active=True)
        .order_by(Video.views.desc())
        .first()
    )
    return video.to_dict() if video else None
