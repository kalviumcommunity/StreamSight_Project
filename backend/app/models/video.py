from datetime import datetime
from app.extensions import db


class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # seconds
    thumbnail_url = db.Column(db.String(500), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    views = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    watch_history = db.relationship("WatchHistory", backref="video", lazy="dynamic", cascade="all, delete-orphan")
    engagements = db.relationship("Engagement", backref="video", lazy="dynamic", cascade="all, delete-orphan")
    bookmarks = db.relationship("Bookmark", backref="video", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_category=True):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category_id": self.category_id,
            "duration": self.duration,
            "thumbnail_url": self.thumbnail_url,
            "video_url": self.video_url,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "views": self.views,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }
        if include_category and self.category:
            data["category"] = self.category.to_dict()
        return data
