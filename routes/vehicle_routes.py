from flask import Blueprint, request
from extensions import db
from models.vehicle import Vehicle
from models.customer import Customer
from utils.validators import get_json_data, require_fields
from utils.error_handlers import bad_request,not_found,conflict
from utils.response import success_response


vehicle_bp = Blueprint("vehicle_bp", __name__, url_prefix="/vehicles")


# ---------------------------
# CREATE VEHICLE
# POST /vehicles
# ---------------------------
@vehicle_bp.route("/", methods=["POST"])
def create_vehicle(): 
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    required_fields = ["customer_id", "vehicle_number", "vehicle_type", "brand", "model"]
    if not require_fields(data, required_fields):
        return bad_request("Missing required vehicle fields")
        
    # CHECK CUSTOMER EXISTS 
    customer = Customer.query.get(data["customer_id"])
    if not customer:
        return not_found("Customer not found")

    # Check duplicate vehicle number
    if Vehicle.query.filter_by(vehicle_number=data["vehicle_number"]).first():
        return conflict("Vehicle number already exists")

    vehicle = Vehicle(
        customer_id=data["customer_id"],
        vehicle_number=data["vehicle_number"],
        vehicle_type=data["vehicle_type"],
        brand=data["brand"],
        model=data["model"]
    )

    
    db.session.add(vehicle)
    db.session.commit()

    return success_response(
    message="Vehicle added successfully",
    data={
        "id": vehicle.id,
        "vehicle_number": vehicle.vehicle_number,
        "customer_id": vehicle.customer_id
    },
    status_code=201
) 


# ---------------------------
# GET ALL VEHICLES
# GET /vehicles
# ---------------------------
@vehicle_bp.route("/", methods=["GET"])
def get_all_vehicles():
    vehicles = Vehicle.query.all()

    vehicles_data = []
    for vehicle in vehicles:
        vehicles_data.append({
            "id": vehicle.id,
            "customer_id": vehicle.customer_id,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "created_at": vehicle.created_at.isoformat()
        })

    return success_response(
        data=vehicles_data,
        status_code=200
    )



# ---------------------------
# GET SINGLE VEHICLE
# GET /vehicles/<id>
# ---------------------------
@vehicle_bp.route("/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return not_found("Vehicle not found")

    return success_response(
        data={
        "id": vehicle.id,
        "customer_id": vehicle.customer_id,
        "vehicle_number": vehicle.vehicle_number,
        "vehicle_type": vehicle.vehicle_type,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "created_at": vehicle.created_at.isoformat()
    },
    status_code=200)


# ---------------------------
# UPDATE VEHICLE
# PUT /vehicles/<id>
# ---------------------------
@vehicle_bp.route("/<int:vehicle_id>", methods=["PUT"])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return not_found("Vehicle not found")

    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    # Prevent duplicate vehicle number on update
    if "vehicle_number" in data:
        existing = Vehicle.query.filter(
            Vehicle.vehicle_number == data["vehicle_number"],
            Vehicle.id != vehicle.id
        ).first()
        if existing:
            return conflict("Vehicle number already exists")
        vehicle.vehicle_number = data["vehicle_number"]

    vehicle.vehicle_type = data.get("vehicle_type", vehicle.vehicle_type)
    vehicle.brand = data.get("brand", vehicle.brand)
    vehicle.model = data.get("model", vehicle.model)

    db.session.commit()

    return success_response(message= "Vehicle updated successfully",status_code=200)


# ---------------------------
# DELETE VEHICLE
# DELETE /vehicles/<id>
# ---------------------------
@vehicle_bp.route("/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return not_found("Vehicle not found")

    db.session.delete(vehicle)
    db.session.commit()

    return success_response(message= "Vehicle deleted successfully",status_code=200)










