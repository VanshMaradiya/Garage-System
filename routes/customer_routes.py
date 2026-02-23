from flask import Blueprint, request, flash
from sqlite3 import IntegrityError
from models.customer import Customer
from extensions import db
from utils.auth import login_required, admin_required
from utils.error_handlers import bad_request,conflict,bad_request
from utils.response import success_response
from utils.validators import get_json_data, require_fields


customer_bp = Blueprint("customer", __name__, url_prefix="/api/customers")


# 🔒 ANY LOGGED-IN USER CAN VIEW CUSTOMERS
@customer_bp.route("", methods=["GET"])
@login_required
def get_customers():
    customers = Customer.query.all()
    data = [
    {
        "id": c.id,
        "name": c.name,
        "phone": c.phone
    } for c in customers
    ]
    
    return success_response(
        message="Customers fetched successfully", 
        data=data
    )

# 🔒 STAFF & ADMIN CAN ADD CUSTOMER
@customer_bp.route("", methods=["POST"])
@login_required
def add_customer():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")
    
    required = ["name", "phone"]
    if not require_fields(data, required):
        return bad_request("Missing required fields: name, phone")

    phone = data.get("phone")

    if not phone:
        return bad_request("Phone number is required")

    # 🔒 CHECK DUPLICATE PHONE (ONLY AT ADD TIME)
    existing_customer = Customer.query.filter_by(phone=phone).first()
    if existing_customer:
        return conflict(
            "Customer with this phone number already exists"
        )

    customer = Customer(
        name=data["name"],
        phone=phone,
        email=data.get("email"),
        address=data.get("address")
    )

    db.session.add(customer)
    db.session.commit()

    return success_response(
    message="Customer created successfully",
    data={
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone
    },
    status_code=201
)


# 🔒 STAFF & ADMIN CAN UPDATE
@customer_bp.route("/<int:id>", methods=["PUT"])
@login_required
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    customer.name = data.get("name", customer.name)
    customer.phone = data.get("phone", customer.phone)
    customer.email = data.get("email", customer.email)
    customer.address = data.get("address", customer.address)

    db.session.commit()
    return success_response(message =  "Customer updated")


# 🔒 ONLY ADMIN CAN DELETE
@customer_bp.route("/<int:id>", methods=["DELETE"])
@login_required
@admin_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash("Customer deleted successfully", "success")

    except IntegrityError:
        db.session.rollback()
        flash(
            "Cannot delete customer because vehicles are associated with this customer",
            "danger"
        )   

    return success_response(message =  "Customer deleted")
