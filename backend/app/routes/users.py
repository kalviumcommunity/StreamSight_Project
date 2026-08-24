from flask import Blueprint, request, jsonify

from app.models import User
from app.utils.decorators import admin_required
from app.utils.validators import validate_pagination
from app.utils.helpers import paginate_query

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("")
@admin_required
def list_users():
    page, per_page = validate_pagination(request.args)
    query = User.query.order_by(User.created_at.desc())
    result = paginate_query(query, page, per_page)
    return jsonify({**result, "items": [u.to_dict() for u in result["items"]]}), 200
