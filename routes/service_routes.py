from flask import Blueprint, request
from datetime import datetime
from extensions import db
from models.service_request import ServiceRequest
from models.vehicle import Vehicle
from models.mechanic import Mechanic
from sqlalchemy.exc import IntegrityError
from utils.validators import get_json_data, require_fields,validate_enum
from utils.error_handlers import bad_request,not_found,server_error
from utils.response import success_response


service_bp = Blueprint("service_bp", __name__, url_prefix="/services")

ALLOWED_STATUS = ["Pending", "In Progress", "Completed"]


# ---------------------------
# CREATE SERVICE REQUEST
# POST /services
# ---------------------------
@service_bp.route("/", methods=["POST"])
def create_service():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    required_fields = [
        "vehicle_id",
        "service_type",
        "service_date",
        "problem_description"
    ]
    if not require_fields(data, required_fields):
        return bad_request("Missing required service fields")

    # Check vehicle exists
    vehicle = Vehicle.query.get(data["vehicle_id"])
    if not vehicle:
        return not_found("Vehicle not found")

    # Validate assigned mechanic (optional)
    assigned_mechanic_id = data.get("assigned_mechanic_id")
    if assigned_mechanic_id:
        mechanic = Mechanic.query.get(assigned_mechanic_id)
        if not mechanic:
            return not_found("Assigned mechanic not found")

    # Convert service_date
    try:
        service_date = datetime.strptime(
            data["service_date"], "%Y-%m-%d"
        ).date()
    except ValueError:
        return bad_request("service_date must be YYYY-MM-DD")

    service = ServiceRequest(
        vehicle_id=data["vehicle_id"],
        service_type=data["service_type"],
        service_date=service_date,
        problem_description=data["problem_description"],
        assigned_mechanic_id=assigned_mechanic_id,
        status="Pending"
    )

    db.session.add(service)
    db.session.commit()

    return success_response(
        message="Service request created",
        data = {
            "id": service.id,
            "status": service.status,
            "assigned_mechanic_id": assigned_mechanic_id
        },
        status_code=201
    )


# ---------------------------
# GET ALL SERVICE REQUESTS
# GET /services
# ---------------------------
@service_bp.route("/", methods=["GET"])
def get_all_services():
    services = ServiceRequest.query.all()

    services_data = []
    for service in services:
        services_data.append({
            "id": service.id,
            "vehicle_id": service.vehicle_id,
            "service_type": service.service_type,
            "service_date": service.service_date.isoformat(),
            "problem_description": service.problem_description,
            "status": service.status,
            "assigned_mechanic_id": service.assigned_mechanic_id,
            "created_at": service.created_at.isoformat()
        })

    return success_response(
        data=services_data,
        status_code=200
    )


# ---------------------------
# GET SINGLE SERVICE REQUEST
# GET /services/<id>
# ---------------------------
@service_bp.route("/<int:service_id>", methods=["GET"])
def get_service(service_id):
    service = ServiceRequest.query.get(service_id)
    if not service:
        return not_found("Service request not found")

    return success_response(
        data={
        "id": service.id,
        "vehicle_id": service.vehicle_id,
        "service_type": service.service_type,
        "service_date": service.service_date.isoformat(),
        "problem_description": service.problem_description,
        "status": service.status,
        "assigned_mechanic_id": service.assigned_mechanic_id,
        "created_at": service.created_at.isoformat()
    },
    status_code=200)


# ---------------------------
# UPDATE SERVICE REQUEST
# PUT /services/<id>
# ---------------------------
@service_bp.route("/<int:service_id>", methods=["PUT"])
def update_service(service_id):
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")
    
    service = ServiceRequest.query.get(service_id)
    if not service:
        return not_found("Service request not found")

    data = request.get_json(silent=True)
    if not data:
        return bad_request("Invalid or missing JSON")

    if "status" in data:
        if not validate_enum(data["status"], ALLOWED_STATUS):
            return bad_request("Invalid service status")

    if "problem_description" in data:
        service.problem_description = data["problem_description"]

    if "assigned_mechanic_id" in data:
        service.assigned_mechanic_id = data["assigned_mechanic_id"]

    db.session.commit()

    return success_response(message="Service status updated successfully")


# ---------------------------
# DELETE SERVICE REQUEST
# DELETE /services/<id>
# ---------------------------
from models.invoice import Invoice

@service_bp.route("/<int:service_id>", methods=["DELETE"])
def delete_service(service_id):
    service = ServiceRequest.query.get(service_id)

    if not service:
        return not_found("Service request not found")

    try:
        db.session.delete(service)
        db.session.commit()

        return success_response(message = "Service request deleted successfully",status_code=200)

    except IntegrityError:
        db.session.rollback()
        return bad_request(
            "Cannot delete service request because an invoice exists for this service",
            )

    except Exception as e:
        db.session.rollback()
        return server_error(
            "Failed to delete service request",
            details= str(e)
        )
