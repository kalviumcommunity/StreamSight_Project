from datetime import datetime
from app.extensions import db
from app.models import Engagement, WatchHistory, WatchSession, Video
from app.utils.errors import NotFoundError, ValidationError


def _get_owned_engagement(engagement_id, user_id):
    engagement = Engagement.query.get(engagement_id)
    if not engagement or engagement.user_id != user_id:
        raise NotFoundError("Engagement session not found")
    return engagement


def start_watch(user_id, video_id):
    video = Video.query.get(video_id)
    if not video or not video.is_active:
        raise NotFoundError("Video not found")

    session = WatchSession(user_id=user_id)
    db.session.add(session)
    db.session.flush()

    engagement = Engagement(
        user_id=user_id,
        video_id=video_id,
        session_id=session.id,
        started_at=datetime.utcnow(),
    )
    db.session.add(engagement)
    db.session.flush()

    history = WatchHistory(
        user_id=user_id,
        video_id=video_id,
        session_id=session.id,
        watch_duration=0,
        completion_rate=0.0,
        completed=False,
    )
    db.session.add(history)

    video.views = (video.views or 0) + 1

    db.session.commit()

    return {
        "session_id": session.id,
        "engagement_id": engagement.id,
        "history_id": history.id,
    }


def record_progress(user_id, engagement_id, watch_duration, completion_rate, seek_count=None):
    engagement = _get_owned_engagement(engagement_id, user_id)

    if watch_duration is not None:
        engagement.watch_duration = max(engagement.watch_duration, int(watch_duration))
    if completion_rate is not None:
        engagement.completion_rate = max(engagement.completion_rate, float(completion_rate))
    if seek_count is not None:
        engagement.seek_count += int(seek_count)

    history = WatchHistory.query.filter_by(session_id=engagement.session_id).first()
    if history:
        history.watch_duration = engagement.watch_duration
        history.completion_rate = engagement.completion_rate

    db.session.commit()
    return engagement.to_dict()


def record_pause(user_id, engagement_id):
    engagement = _get_owned_engagement(engagement_id, user_id)
    engagement.pause_count += 1
    db.session.commit()
    return engagement.to_dict()


def record_complete(user_id, engagement_id):
    engagement = _get_owned_engagement(engagement_id, user_id)

    if engagement.completion_rate >= 95:
        engagement.replay_count += 1

    engagement.completion_rate = 100.0

    history = WatchHistory.query.filter_by(session_id=engagement.session_id).first()
    if history:
        if history.completed:
            engagement.replay_count = max(engagement.replay_count, 1)
        history.completion_rate = 100.0
        history.completed = True

    db.session.commit()
    return engagement.to_dict()


def end_watch(user_id, engagement_id):
    engagement = _get_owned_engagement(engagement_id, user_id)
    engagement.ended_at = datetime.utcnow()

    session = WatchSession.query.get(engagement.session_id)
    if session:
        session.session_end = engagement.ended_at
        started = session.session_start or engagement.started_at
        if started:
            delta = (session.session_end - started).total_seconds()
            session.session_duration = max(0, int(delta))

    db.session.commit()
    return {
        "engagement": engagement.to_dict(),
        "session": session.to_dict() if session else None,
    }
