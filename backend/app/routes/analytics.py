from flask import Blueprint, request, jsonify

from app.services import analytics_service
from app.utils.decorators import admin_required
from app.utils.helpers import parse_date_range

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _filters():
    date_from, date_to = parse_date_range(request.args)
    category_id = request.args.get("category_id")
    video_id = request.args.get("video_id")
    return (
        date_from,
        date_to,
        int(category_id) if category_id else None,
        int(video_id) if video_id else None,
    )


@bp.get("/summary")
@admin_required
def summary():
    date_from, date_to, category_id, video_id = _filters()
    return jsonify(analytics_service.summary_metrics(date_from, date_to, category_id, video_id)), 200


@bp.get("/content")
@admin_required
def content():
    date_from, date_to, category_id, video_id = _filters()
    return jsonify(analytics_service.content_performance(date_from, date_to, category_id, video_id)), 200


@bp.get("/dropoff")
@admin_required
def dropoff():
    date_from, date_to, category_id, video_id = _filters()
    return jsonify(analytics_service.dropoff_analysis(date_from, date_to, category_id, video_id)), 200


@bp.get("/trending")
@admin_required
def trending():
    period = request.args.get("period", "weekly")
    limit = int(request.args.get("limit", 10))
    return jsonify(analytics_service.trending_content(period, limit)), 200


@bp.get("/categories")
@admin_required
def categories():
    date_from, date_to, _, _ = _filters()
    return jsonify(analytics_service.category_analytics(date_from, date_to)), 200


@bp.get("/searches")
@admin_required
def searches():
    limit = int(request.args.get("limit", 10))
    return jsonify(analytics_service.search_analytics(limit)), 200


@bp.get("/search-trends")
@admin_required
def search_trends_route():
    period = request.args.get("period", "daily")
    return jsonify(analytics_service.search_trends(period)), 200


@bp.get("/trends")
@admin_required
def trends():
    period = request.args.get("period", "daily")
    date_from, date_to, _, _ = _filters()
    return jsonify(analytics_service.engagement_trends(period, date_from, date_to)), 200


@bp.get("/acquisition-insights")
@admin_required
def acquisition_insights():
    date_from, date_to, _, _ = _filters()
    insights = analytics_service.acquisition_insights(date_from, date_to)
    insights["summary"] = analytics_service.acquisition_summary(date_from, date_to)
    return jsonify(insights), 200
