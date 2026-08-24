from datetime import datetime
from app.extensions import db


class SearchActivity(db.Model):
    __tablename__ = "search_activity"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    search_query = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    result_count = db.Column(db.Integer, default=0, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "search_query": self.search_query,
            "category": self.category,
            "result_count": self.result_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
