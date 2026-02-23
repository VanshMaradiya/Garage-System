# routes/invoice_routes.py

from flask import Blueprint, request
from extensions import db
from models.invoice import Invoice
from utils.error_handlers import bad_request,conflict,bad_request
from utils.response import success_response
from utils.validators import get_json_data

invoice_bp = Blueprint("invoice", __name__, url_prefix="/api/invoices")


# ✅ Create Invoice
@invoice_bp.route("/create", methods=["POST"])
def create_invoice():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    # 🔒 STEP 1: Check duplicate invoice
    service_id = data.get("service_id")

    existing_invoice = Invoice.query.filter_by(
        service_id=service_id
    ).first()

    if existing_invoice:
        return conflict (
            "Invoice already exists for this service",
            invoice_id = existing_invoice.id
        )
    
    # Validate amount
    try:
        total_amount = float(data["total_amount"])
        if total_amount <= 0:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        return bad_request("Amount must be a positive number")
    
    try:
        invoice = Invoice(
            service_id=data["service_id"],
            customer_id=data["customer_id"],
            vehicle_id=data["vehicle_id"],
            total_amount=data["total_amount"],
            payment_status=data.get("payment_status", "Pending")
        )
        

        db.session.add(invoice)
        db.session.commit()

        return success_response(
            message = "Invoice created successfully",
            data= {
                "invoice_id": invoice.id,
                "amount": invoice.total_amount
            },
            status_code=201
        )

    except Exception as e:
        db.session.rollback()
        return bad_request(str(e))


# ✅ Get All Invoices
@invoice_bp.route("/", methods=["GET"])
def get_all_invoices():
    invoices = Invoice.query.all()

    result = []
    for inv in invoices:
        result.append({
            "id": inv.id,
            "service_id": inv.service_id,
            "customer_id": inv.customer_id,
            "vehicle_id": inv.vehicle_id,
            "total_amount": inv.total_amount,
            "payment_status": inv.payment_status,
            "created_at": inv.created_at
        })

    return success_response(result)


# ✅ Get Single Invoice
@invoice_bp.route("/<int:id>", methods=["GET"])
def get_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    return success_response(
        data= {
        "id": invoice.id,
        "service_id": invoice.service_id,
        "customer_id": invoice.customer_id,
        "vehicle_id": invoice.vehicle_id,
        "total_amount": invoice.total_amount,
        "payment_status": invoice.payment_status,
        "created_at": invoice.created_at
        },
        status_code=200)


#  Update Payment Status
@invoice_bp.route("/update/<int:id>", methods=["PUT"])
def update_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    invoice.payment_status = data.get("payment_status", invoice.payment_status)

    db.session.commit()

    return success_response(message = "Invoice updated successfully",status_code=200)


#  Delete Invoice
@invoice_bp.route("/delete/<int:id>", methods=["DELETE"])
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    db.session.delete(invoice)
    db.session.commit()

    return success_response(message= "Invoice deleted successfully",status_code=200)


