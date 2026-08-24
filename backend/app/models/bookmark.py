from datetime import datetime
from app.extensions import db


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    __table_args__ = (db.UniqueConstraint("user_id", "video_id", name="uq_user_video_bookmark"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey("videos.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    def to_dict(self, include_video=True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "video_id": self.video_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_video and self.video:
            data["video"] = self.video.to_dict()
        return data
