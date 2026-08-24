"""
Engagement-Based Retention Score
---------------------------------
This is a transparent, formula-driven score (0-100) derived purely from
observed viewer engagement signals. It is NOT a scientifically validated
predictive model of future retention - it is a weighted composite of
engagement signals used to rank/compare content and viewers.

Retention Score =
    (
        normalized_watch_duration   * 0.35 +
        normalized_completion_rate  * 0.35 +
        normalized_session_duration * 0.20 +
        normalized_repeat_views     * 0.10
    ) * 100

Where each component is normalized to a 0-1 range:
  - normalized_watch_duration:   avg_watch_duration / avg_video_duration (capped at 1)
  - normalized_completion_rate:  avg_completion_rate / 100
  - normalized_session_duration: avg_session_duration / SESSION_DURATION_CAP (capped at 1)
  - normalized_repeat_views:     repeat_view_count / REPEAT_VIEW_CAP (capped at 1)
"""

SESSION_DURATION_CAP_SECONDS = 3600  # 1 hour session treated as "full" engagement
REPEAT_VIEW_CAP = 3  # 3+ repeat views treated as "full" repeat engagement

WEIGHT_WATCH_DURATION = 0.35
WEIGHT_COMPLETION_RATE = 0.35
WEIGHT_SESSION_DURATION = 0.20
WEIGHT_REPEAT_VIEWS = 0.10


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def calculate_retention_score(
    avg_watch_duration,
    avg_video_duration,
    avg_completion_rate,
    avg_session_duration,
    repeat_view_count,
):
    normalized_watch_duration = _clamp(
        (avg_watch_duration / avg_video_duration) if avg_video_duration else 0
    )
    normalized_completion_rate = _clamp((avg_completion_rate or 0) / 100)
    normalized_session_duration = _clamp(
        (avg_session_duration or 0) / SESSION_DURATION_CAP_SECONDS
    )
    normalized_repeat_views = _clamp((repeat_view_count or 0) / REPEAT_VIEW_CAP)

    score = (
        normalized_watch_duration * WEIGHT_WATCH_DURATION
        + normalized_completion_rate * WEIGHT_COMPLETION_RATE
        + normalized_session_duration * WEIGHT_SESSION_DURATION
        + normalized_repeat_views * WEIGHT_REPEAT_VIEWS
    ) * 100

    return round(score, 2)


def classify_acquisition_recommendation(metrics):
    """
    metrics: dict with keys completion_rate, pause_frequency, watch_duration,
    avg_video_duration, retention_score, repeat_view_ratio, views, dropoff_early_pct
    Returns (label, reason) or None if it doesn't clearly fit a bucket.
    """
    completion_rate = metrics.get("completion_rate", 0)
    pause_frequency = metrics.get("pause_frequency", 0)
    retention_score = metrics.get("retention_score", 0)
    repeat_view_ratio = metrics.get("repeat_view_ratio", 0)
    views = metrics.get("views", 0)
    dropoff_early_pct = metrics.get("dropoff_early_pct", 0)

    if (
        completion_rate >= 70
        and pause_frequency <= 2
        and retention_score >= 65
        and repeat_view_ratio >= 0.15
    ):
        return (
            "Strong Acquisition Candidate",
            "High completion rate, low pause frequency, and strong repeat viewing "
            "indicate strong viewer engagement and retention potential.",
        )

    if (
        views >= 20
        and completion_rate < 40
        and (pause_frequency > 3 or dropoff_early_pct > 40)
    ):
        return (
            "Needs Investigation",
            "High view count paired with low completion and heavy early drop-off "
            "suggests the content is attracting viewers but failing to hold them.",
        )

    if (
        views < 20
        and completion_rate >= 70
        and retention_score >= 65
        and repeat_view_ratio >= 0.15
    ):
        return (
            "Hidden Performer",
            "Despite lower total views, this content shows very high completion, "
            "retention, and repeat viewing - a strong candidate for more promotion.",
        )

    return None
