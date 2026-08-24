from flask import Blueprint, request, jsonify

from app.models import Engagement
from app.services.import_service import import_engagement_data
from app.utils.decorators import admin_required
from app.utils.validators import validate_pagination
from app.utils.helpers import paginate_query
from app.utils.errors import ValidationError

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/engagement")
@admin_required
def list_engagement():
    page, per_page = validate_pagination(request.args)
    query = Engagement.query.order_by(Engagement.created_at.desc())
    result = paginate_query(query, page, per_page)
    return jsonify({**result, "items": [e.to_dict() for e in result["items"]]}), 200


@bp.post("/import/engagement")
@admin_required
def import_engagement():
    if "file" not in request.files:
        raise ValidationError("No file provided under form field 'file'")
    file_storage = request.files["file"]
    if not file_storage.filename:
        raise ValidationError("No file selected")

    report = import_engagement_data(file_storage)
    return jsonify(report), 200
