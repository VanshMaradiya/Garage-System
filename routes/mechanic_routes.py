# routes/mechanic_routes.py

from flask import Blueprint, request
from extensions import db
from models.mechanic import Mechanic
from utils.error_handlers import bad_request
from utils.response import success_response
from utils.validators import get_json_data

mechanic_bp = Blueprint("mechanic", __name__, url_prefix="/api/mechanics")


# ✅ Create Mechanic
@mechanic_bp.route("/create", methods=["POST"])
def create_mechanic():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    try:
        mechanic = Mechanic(
            name=data["name"],
            phone=data["phone"],
            specialization=data.get("specialization"),
            is_available=data.get("is_available", True)
        )

        db.session.add(mechanic)
        db.session.commit()

        return success_response(
            message="Mechanic created successfully",
            data={
                "id": mechanic.id,
                "name": mechanic.name,
                "specialization": mechanic.specialization
            },
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return bad_request(str(e))


# ✅ Get All Mechanics
@mechanic_bp.route("/", methods=["GET"])
def get_all_mechanics():
    mechanics = Mechanic.query.all()

    result = []
    for m in mechanics:
        result.append({
            "id": m.id,
            "name": m.name,
            "phone": m.phone,
            "specialization": m.specialization,
            "is_available": m.is_available,
            "created_at": m.created_at
        })

    return success_response(result,status_code=200)


# ✅ Get Single Mechanic
@mechanic_bp.route("/<int:id>", methods=["GET"])
def get_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)

    return success_response(
        data={
        "id": mechanic.id,
        "name": mechanic.name,
        "phone": mechanic.phone,
        "specialization": mechanic.specialization,
        "is_available": mechanic.is_available,
        "created_at": mechanic.created_at
    },
    status_code=200)


# ✅ Update Mechanic
@mechanic_bp.route("/update/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    mechanic.name = data.get("name", mechanic.name)
    mechanic.phone = data.get("phone", mechanic.phone)
    mechanic.specialization = data.get("specialization", mechanic.specialization)
    mechanic.is_available = data.get("is_available", mechanic.is_available)

    db.session.commit()

    return success_response(message= "Mechanic updated successfully",status_code=200)


# ✅ Delete Mechanic
@mechanic_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)

    db.session.delete(mechanic)
    db.session.commit()

    return success_response(message= "Mechanic deleted successfully",status_code=200)
