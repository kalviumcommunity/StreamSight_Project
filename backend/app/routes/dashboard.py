from flask import Blueprint, jsonify

from app.services.analytics_service import dashboard_overview
from app.utils.decorators import admin_required

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("/overview")
@admin_required
def overview():
    return jsonify(dashboard_overview()), 200
