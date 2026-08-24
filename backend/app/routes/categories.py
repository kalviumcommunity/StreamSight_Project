from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Category, Video
from app.utils.decorators import admin_required
from app.utils.validators import require_fields, validate_pagination
from app.utils.helpers import paginate_query
from app.utils.errors import NotFoundError, ConflictError

bp = Blueprint("categories", __name__, url_prefix="/api/categories")


@bp.get("")
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify([c.to_dict() for c in categories]), 200


@bp.get("/<int:category_id>")
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError("Category not found")
    return jsonify(category.to_dict()), 200


@bp.get("/<int:category_id>/videos")
def category_videos(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError("Category not found")

    page, per_page = validate_pagination(request.args)
    query = Video.query.filter_by(category_id=category_id, is_active=True).order_by(Video.created_at.desc())
    result = paginate_query(query, page, per_page)
    return jsonify({
        **result,
        "items": [v.to_dict(include_category=False) for v in result["items"]],
    }), 200


@bp.post("")
@admin_required
def create_category():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])
    if Category.query.filter_by(name=data["name"]).first():
        raise ConflictError("Category already exists")
    category = Category(name=data["name"].strip(), description=data.get("description"))
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


@bp.put("/<int:category_id>")
@admin_required
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError("Category not found")
    data = request.get_json(silent=True) or {}
    if "name" in data:
        category.name = data["name"].strip()
    if "description" in data:
        category.description = data["description"]
    db.session.commit()
    return jsonify(category.to_dict()), 200


@bp.delete("/<int:category_id>")
@admin_required
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        raise NotFoundError("Category not found")
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200
