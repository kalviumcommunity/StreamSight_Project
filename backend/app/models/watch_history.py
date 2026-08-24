from datetime import datetime
from app.extensions import db


class WatchHistory(db.Model):
    __tablename__ = "watch_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    watched_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    watch_duration = db.Column(db.Integer, default=0, nullable=False)  # seconds
    completion_rate = db.Column(db.Float, default=0.0, nullable=False)  # 0-100
    completed = db.Column(db.Boolean, default=False, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("watch_sessions.id"), nullable=True)

    def to_dict(self, include_video=True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "video_id": self.video_id,
            "watched_at": self.watched_at.isoformat() if self.watched_at else None,
            "watch_duration": self.watch_duration,
            "completion_rate": self.completion_rate,
            "completed": self.completed,
            "session_id": self.session_id,
        }
        if include_video and self.video:
            data["video"] = self.video.to_dict()
        return data
