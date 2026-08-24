"""
Seed StreamSight with realistic demo data so the analytics dashboard has
something meaningful to show.

Engagement is generated per a viewer "profile" (high / medium / low) so
that watch duration, completion rate, pause frequency, and repeat views
move together logically instead of being independently random:

  - high engagement:   high completion, high watch time, few pauses, some replays
  - medium engagement:  moderate completion, moderate pauses, rare replays
  - low engagement:    low completion, frequent pauses, no replays

Run with:  python seed/seed_data.py
"""
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import (
    User, Role, Category, Video, WatchHistory, Engagement,
    Bookmark, SearchActivity, WatchSession,
)

random.seed(42)

CATEGORIES = [
    ("Action", "High-octane stunts, chases, and adrenaline-fueled storylines."),
    ("Comedy", "Light-hearted shows and films designed to entertain and amuse."),
    ("Drama", "Character-driven stories exploring real emotional stakes."),
    ("Thriller", "Suspenseful, tension-filled narratives full of twists."),
    ("Sci-Fi", "Futuristic and speculative fiction exploring technology and space."),
    ("Documentary", "Non-fiction storytelling covering real people and events."),
    ("Romance", "Stories centered on relationships and emotional connection."),
]

VIDEO_TITLE_PARTS = [
    "Shadow", "Horizon", "Midnight", "Echo", "Crimson", "Silent", "Rising",
    "Distant", "Hidden", "Fractured", "Golden", "Last", "Broken", "Eternal",
    "Wild", "Quiet", "Neon", "Forgotten", "Restless", "Radiant",
]
VIDEO_TITLE_NOUNS = [
    "Signal", "City", "Protocol", "Harbor", "Frontier", "Legacy", "Descent",
    "Origins", "Pursuit", "Kingdom", "Verdict", "Voyage", "Reckoning",
    "Season", "Chronicles", "Dawn", "Circuit", "Anthem", "Exile", "Current",
]

SEARCH_TERMS = [
    "thriller", "comedy", "sci-fi", "action movies", "drama series",
    "documentary", "romance", "space", "true crime", "detective",
    "superhero", "zombie", "musical", "war", "unknown show xyz",
]

FIRST_NAMES = [
    "Ava", "Liam", "Noah", "Emma", "Oliver", "Sophia", "Elijah", "Isabella",
    "Mason", "Mia", "Lucas", "Amelia", "Ethan", "Harper", "James", "Evelyn",
    "Benjamin", "Abigail", "Henry", "Emily", "Alexander", "Ella", "Michael",
    "Scarlett", "Daniel", "Grace", "Jacob", "Chloe", "Logan", "Victoria",
]

NUM_USERS = 30
NUM_VIDEOS_PER_CATEGORY = 5
DAYS_OF_HISTORY = 60

PROFILE_WEIGHTS = [("high", 0.25), ("medium", 0.5), ("low", 0.25)]


def weighted_profile():
    r = random.random()
    cumulative = 0
    for profile, weight in PROFILE_WEIGHTS:
        cumulative += weight
        if r <= cumulative:
            return profile
    return "medium"


def random_datetime_within(days):
    delta_seconds = random.randint(0, days * 24 * 3600)
    return datetime.utcnow() - timedelta(seconds=delta_seconds)


def build_categories():
    categories = []
    for name, description in CATEGORIES:
        category = Category(name=name, description=description)
        db.session.add(category)
        categories.append(category)
    db.session.flush()
    return categories


def build_videos(categories):
    videos = []
    used_titles = set()
    for category in categories:
        for _ in range(NUM_VIDEOS_PER_CATEGORY):
            while True:
                title = f"{random.choice(VIDEO_TITLE_PARTS)} {random.choice(VIDEO_TITLE_NOUNS)}"
                if title not in used_titles:
                    used_titles.add(title)
                    break
            duration = random.choice([1200, 1500, 1800, 2400, 3000, 3600])  # 20-60 min
            release_offset = random.randint(0, 700)
            video = Video(
                title=title,
                description=f"A {category.name.lower()} story about {title.lower()}.",
                category_id=category.id,
                duration=duration,
                thumbnail_url=f"https://picsum.photos/seed/{title.replace(' ', '')}/400/225",
                video_url=f"https://cdn.streamsight.example/videos/{title.replace(' ', '-').lower()}.mp4",
                release_date=(datetime.utcnow() - timedelta(days=release_offset)).date(),
                views=0,
            )
            db.session.add(video)
            videos.append(video)
    db.session.flush()
    return videos


def build_users():
    admin = User(name="Subhadeep Samanta", email="subhadeepsamanta1535@gmail.com", role=Role.ADMIN)
    admin.set_password("Subhadeep@123")
    db.session.add(admin)

    users = []
    for i, name in enumerate(FIRST_NAMES[:NUM_USERS]):
        user = User(
            name=f"{name} Viewer",
            email=f"{name.lower()}{i}@streamsight.io",
            role=Role.USER,
            created_at=random_datetime_within(200),
        )
        user.set_password("Password123!")
        user.profile = weighted_profile()
        db.session.add(user)
        users.append(user)
    db.session.flush()
    return admin, users


def profile_engagement_values(profile, video_duration):
    if profile == "high":
        completion_rate = random.uniform(75, 100)
        pause_count = random.randint(0, 2)
        replay_chance = 0.25
    elif profile == "medium":
        completion_rate = random.uniform(40, 75)
        pause_count = random.randint(2, 5)
        replay_chance = 0.05
    else:
        completion_rate = random.uniform(5, 40)
        pause_count = random.randint(4, 10)
        replay_chance = 0.0

    watch_duration = int(video_duration * (completion_rate / 100) * random.uniform(0.95, 1.05))
    watch_duration = max(0, min(watch_duration, video_duration))
    replay_count = 1 if (completion_rate >= 90 and random.random() < replay_chance) else 0
    seek_count = random.randint(0, 3) if profile != "low" else random.randint(0, 1)

    return {
        "completion_rate": round(completion_rate, 2),
        "pause_count": pause_count,
        "watch_duration": watch_duration,
        "replay_count": replay_count,
        "seek_count": seek_count,
    }


def build_watch_activity(users, videos):
    for user in users:
        profile = getattr(user, "profile", "medium")
        num_watches = {
            "high": random.randint(15, 30),
            "medium": random.randint(8, 18),
            "low": random.randint(3, 10),
        }[profile]

        watched_videos = random.choices(videos, k=num_watches)

        for video in watched_videos:
            values = profile_engagement_values(profile, video.duration)
            watched_at = random_datetime_within(DAYS_OF_HISTORY)

            session_padding = random.randint(10, 120)
            session_duration = values["watch_duration"] + session_padding
            session = WatchSession(
                user_id=user.id,
                session_start=watched_at,
                session_end=watched_at + timedelta(seconds=session_duration),
                session_duration=session_duration,
            )
            db.session.add(session)
            db.session.flush()

            engagement = Engagement(
                user_id=user.id,
                video_id=video.id,
                session_id=session.id,
                watch_duration=values["watch_duration"],
                pause_count=values["pause_count"],
                completion_rate=values["completion_rate"],
                replay_count=values["replay_count"],
                seek_count=values["seek_count"],
                started_at=watched_at,
                ended_at=watched_at + timedelta(seconds=session_duration),
                created_at=watched_at,
            )
            db.session.add(engagement)

            history = WatchHistory(
                user_id=user.id,
                video_id=video.id,
                session_id=session.id,
                watched_at=watched_at,
                watch_duration=values["watch_duration"],
                completion_rate=values["completion_rate"],
                completed=values["completion_rate"] >= 90,
            )
            db.session.add(history)

            video.views = (video.views or 0) + 1

            if profile == "high" and random.random() < 0.35:
                exists = Bookmark.query.filter_by(user_id=user.id, video_id=video.id).first()
                if not exists:
                    db.session.add(Bookmark(user_id=user.id, video_id=video.id, created_at=watched_at))

        num_searches = random.randint(1, 6)
        for _ in range(num_searches):
            term = random.choice(SEARCH_TERMS)
            matches = sum(1 for v in videos if term.split()[0].lower() in v.title.lower())
            db.session.add(SearchActivity(
                user_id=user.id,
                search_query=term,
                category=random.choice(CATEGORIES)[0] if random.random() < 0.5 else None,
                result_count=matches,
                timestamp=random_datetime_within(DAYS_OF_HISTORY),
            ))

    db.session.commit()


def run():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Seeding categories...")
        categories = build_categories()

        print("Seeding videos...")
        videos = build_videos(categories)

        print("Seeding users...")
        admin, users = build_users()

        print("Seeding watch activity, engagement, bookmarks, and searches...")
        build_watch_activity(users, videos)

        print("Done.")
        print(f"  Categories: {len(categories)}")
        print(f"  Videos: {len(videos)}")
        print(f"  Users: {len(users) + 1} (including 1 admin)")
        print("  Admin login: subhadeepsamanta1535@gmail.com / Subhadeep@123")
        print("  Sample user login: (any seeded user)@streamsight.io / Password123!")


if __name__ == "__main__":
    run()
