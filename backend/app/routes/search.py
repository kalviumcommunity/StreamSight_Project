from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import Video, SearchActivity
from app.utils.validators import validate_pagination
from app.utils.helpers import paginate_query
from app.utils.errors import ValidationError

bp = Blueprint("search", __name__, url_prefix="/api/search")


def _current_user_id_optional():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return int(identity) if identity else None
    except Exception:
        return None


@bp.get("")
def search_videos():
    q = (request.args.get("q") or "").strip()
    if not q:
        raise ValidationError("Query parameter 'q' is required")

    page, per_page = validate_pagination(request.args)
    category_id = request.args.get("category_id")
    sort = request.args.get("sort", "relevance")

    query = Video.query.filter(Video.is_active.is_(True), Video.title.ilike(f"%{q}%"))
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    if sort == "views":
        query = query.order_by(Video.views.desc())
    elif sort == "newest":
        query = query.order_by(Video.created_at.desc())

    result = paginate_query(query, page, per_page)

    activity = SearchActivity(
        user_id=_current_user_id_optional(),
        search_query=q,
        category=request.args.get("category"),
        result_count=result["total"],
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({**result, "items": [v.to_dict() for v in result["items"]]}), 200
