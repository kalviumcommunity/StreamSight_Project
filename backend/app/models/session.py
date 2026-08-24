from datetime import datetime
from app.extensions import db


class WatchSession(db.Model):
    __tablename__ = "watch_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_start = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    session_end = db.Column(db.DateTime, nullable=True)
    session_duration = db.Column(db.Integer, default=0, nullable=False)  # seconds

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_start": self.session_start.isoformat() if self.session_start else None,
            "session_end": self.session_end.isoformat() if self.session_end else None,
            "session_duration": self.session_duration,
        }
