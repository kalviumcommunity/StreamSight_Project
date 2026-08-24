from datetime import datetime
from app.extensions import db


class Engagement(db.Model):
    __tablename__ = "engagements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("watch_sessions.id"), nullable=True)
    watch_duration = db.Column(db.Integer, default=0, nullable=False)  # seconds
    pause_count = db.Column(db.Integer, default=0, nullable=False)
    completion_rate = db.Column(db.Float, default=0.0, nullable=False)  # 0-100
    replay_count = db.Column(db.Integer, default=0, nullable=False)
    seek_count = db.Column(db.Integer, default=0, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    ended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "video_id": self.video_id,
            "session_id": self.session_id,
            "watch_duration": self.watch_duration,
            "pause_count": self.pause_count,
            "completion_rate": self.completion_rate,
            "replay_count": self.replay_count,
            "seek_count": self.seek_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
