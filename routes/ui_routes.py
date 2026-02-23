from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models.user import User
from models.customer import Customer
from models.vehicle import Vehicle
from models.service_request import ServiceRequest
from models.mechanic import Mechanic
from models.invoice import Invoice
from functools import wraps
from sqlalchemy.exc import IntegrityError

ui = Blueprint("ui", __name__)

# ---------- AUTH HELPERS ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "danger")
            return redirect(url_for("ui.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = User.query.get(session.get("user_id"))

            if not user or user.role not in roles:
                flash("Access denied", "danger")
                return redirect(url_for("ui.dashboard"))

            return view(*args, **kwargs)
        return wrapped
    return decorator

@ui.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None

# ---------- login required helper ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("ui.login"))
        return view(*args, **kwargs)
    return wrapped

@ui.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None


# ---------- Dashboard ----------
@ui.route("/")
@login_required
def dashboard():
    total_customers = Customer.query.count()
    total_vehicles = Vehicle.query.count()
    total_mechanics = Mechanic.query.count()

    available_mechanics = Mechanic.query.filter_by(is_available=True).count()

    pending_services = ServiceRequest.query.filter_by(status="Pending").count()
    completed_services = ServiceRequest.query.filter_by(status="Completed").count()

    total_invoices = Invoice.query.count()
    paid_invoices = Invoice.query.filter_by(payment_status="Paid").count()
    pending_invoices = Invoice.query.filter_by(payment_status="Pending").count()

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        total_vehicles=total_vehicles,
        total_mechanics=total_mechanics,
        available_mechanics=available_mechanics,
        pending_services=pending_services,
        completed_services=completed_services,
        total_invoices=total_invoices,
        paid_invoices=paid_invoices,
        pending_invoices=pending_invoices
    )

# ---------- Register ----------
@ui.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
            role=request.form.get("role", "admin")
        )
        user.set_password(request.form["password"])

        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("ui.login"))

    return render_template("auth/register.html")

# ---------- Login ----------
@ui.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and user.check_password(request.form["password"]):
            session["user_id"] = user.id
            flash("Login successful", "success")
            return redirect(url_for("ui.dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("auth/login.html")

# ---------- Logout ----------
@ui.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "success")
    return redirect(url_for("ui.login"))


# ---------- Customers ----------
@ui.route("/customers")
@login_required
@role_required("admin")
def customers_list():
    customers = Customer.query.all()
    return render_template("customers/list.html", customers=customers)

@ui.route("/customers/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def customers_create():
    if request.method == "POST":
        phone = request.form["phone"]

        # 🔒 DUPLICATE PHONE CHECK (CRITICAL)
        existing_customer = Customer.query.filter_by(phone=phone).first()
        if existing_customer:
            flash(
                "Customer with this phone number already exists",
                "danger"
            )
            return redirect(url_for("ui.customers_create"))

        customer = Customer(
            name=request.form["name"],
            phone=phone,
            email=request.form.get("email"),
            address=request.form.get("address")
        )

        db.session.add(customer)
        db.session.commit()

        flash("Customer created successfully", "success")
        return redirect(url_for("ui.customers_list"))

    return render_template("customers/create.html")

@ui.route("/customers/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def customers_update(id):
    customer = Customer.query.get_or_404(id)

    if request.method == "POST":
        customer.name = request.form["name"]
        customer.phone = request.form["phone"]
        customer.email = request.form.get("email")
        customer.address = request.form.get("address")

        db.session.commit()
        flash("Customer updated successfully", "success")
        return redirect(url_for("ui.customers_list"))

    return render_template("customers/update.html", customer=customer)

@ui.route("/customers/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def customers_delete(id):
    customer = Customer.query.get_or_404(id)
    
    #  PRE-CHECK (THIS IS THE REAL FIX)
    has_vehicles = Vehicle.query.filter_by(customer_id=id).first()
    
    if has_vehicles:
        flash(
            "Cannot delete customer because vehicles are associated with this customer",
            "danger"
        )
        return redirect(url_for("ui.customers_list"))
    
    db.session.delete(customer)
    db.session.commit()

    flash("Customer deleted successfully", "success")
    return redirect(url_for("ui.customers_list"))

# ---------- Vehicles ----------
@ui.route("/vehicles")
@login_required
def vehicles_list():
    vehicles = Vehicle.query.all()
    return render_template("vehicles/list.html", vehicles=vehicles)

@ui.route("/vehicles/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def vehicles_create():
    customers = Customer.query.all()

    if request.method == "POST":
        vehicle_number = request.form["vehicle_number"]

        # 🔒 PRE-CHECK: Duplicate vehicle number (UI level)
        existing_vehicle = Vehicle.query.filter_by(
            vehicle_number=vehicle_number
        ).first()

        if existing_vehicle:
            flash(
                "Vehicle with this number already exists",
                "danger"
            )
            return redirect(url_for("ui.vehicles_create"))

        vehicle = Vehicle(
            customer_id=request.form["customer_id"],
            vehicle_number=vehicle_number,
            vehicle_type=request.form["vehicle_type"],
            brand=request.form.get("brand"),
            model=request.form.get("model")
        )

        try:
            db.session.add(vehicle)
            db.session.commit()
            flash("Vehicle created successfully", "success")
            return redirect(url_for("ui.vehicles_list"))

        except IntegrityError:
            db.session.rollback()
            flash(
                "Vehicle number already exists",
                "danger"
            )
            return redirect(url_for("ui.vehicles_create"))

    return render_template(
        "vehicles/create.html",
        customers=customers
    )

@ui.route("/vehicles/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def vehicles_update(id):
    vehicle = Vehicle.query.get_or_404(id)
    customers = Customer.query.all()

    if request.method == "POST":
        # Prevent duplicate vehicle number (same as API logic)
        existing = Vehicle.query.filter(
            Vehicle.vehicle_number == request.form["vehicle_number"],
            Vehicle.id != vehicle.id
        ).first()
        if existing:
            flash("Vehicle number already exists", "danger")
            return redirect(url_for("ui.vehicles_update", id=id))

        vehicle.vehicle_number = request.form["vehicle_number"]
        vehicle.vehicle_type = request.form["vehicle_type"]
        vehicle.brand = request.form.get("brand")
        vehicle.model = request.form.get("model")
        vehicle.customer_id = request.form["customer_id"]

        db.session.commit()
        flash("Vehicle updated successfully", "success")
        return redirect(url_for("ui.vehicles_list"))

    return render_template(
        "vehicles/update.html",
        vehicle=vehicle,
        customers=customers
    )

@ui.route("/vehicles/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def vehicles_delete(id):
    vehicle = Vehicle.query.get_or_404(id)

    db.session.delete(vehicle)
    db.session.commit()

    flash("Vehicle deleted successfully", "success")
    return redirect(url_for("ui.vehicles_list"))


# ---------- Services ----------
@ui.route("/services")
@login_required
@role_required("admin", "staff")
def services_list():
    services = ServiceRequest.query.all()
    return render_template("services/list.html", services=services)

@ui.route("/services/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def services_create():
    vehicles = Vehicle.query.all()
    mechanics = Mechanic.query.filter_by(is_available=True).all()

    if request.method == "POST":
        mechanic_id = request.form.get("mechanic_id")

        # 🔒 BACKEND VALIDATION (IMPORTANT)
        mechanic = None
        if mechanic_id:
            mechanic = Mechanic.query.get(mechanic_id)

            if not mechanic or not mechanic.is_available:
                flash("Selected mechanic is not available", "danger")
                return redirect(url_for("ui.services_create"))

        service = ServiceRequest(
            vehicle_id=request.form["vehicle_id"],
            service_type=request.form["service_type"],
            service_date=request.form["service_date"],
            problem_description=request.form["problem_description"],
            assigned_mechanic_id=mechanic_id
        )

        db.session.add(service)

        # 🔄 AUTO UPDATE MECHANIC AVAILABILITY
        if mechanic:
            mechanic.is_available = False

        db.session.commit()

        flash("Service request created successfully", "success")
        return redirect(url_for("ui.services_list"))

    return render_template(
        "services/create.html",
        vehicles=vehicles,
        mechanics=mechanics
    )

@ui.route("/services/<int:service_id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def services_update(service_id):
    service = ServiceRequest.query.get_or_404(service_id)
    vehicles = Vehicle.query.all()
    mechanics = Mechanic.query.all()

    if request.method == "POST":
        old_mechanic_id = service.assigned_mechanic_id

        new_mechanic_id = request.form.get("mechanic_id")
        new_status = request.form.get("status")

        # 🔒 VALIDATE MECHANIC
        new_mechanic = None
        if new_mechanic_id:
            new_mechanic = Mechanic.query.get(new_mechanic_id)

            if not new_mechanic:
                flash("Invalid mechanic selected", "danger")
                return redirect(url_for("ui.services_update", service_id=service_id))

            # Prevent assigning unavailable mechanic (unless same mechanic)
            if (
                old_mechanic_id != int(new_mechanic_id)
                and not new_mechanic.is_available
            ):
                flash("Selected mechanic is not available", "danger")
                return redirect(url_for("ui.services_update", service_id=service_id))

        # 🔄 RESTORE OLD MECHANIC
        if old_mechanic_id:
            old_mechanic = Mechanic.query.get(old_mechanic_id)

            if old_mechanic:
                # If service completed OR mechanic changed
                if new_status == "Completed" or (
                    new_mechanic_id and int(new_mechanic_id) != old_mechanic_id
                ):
                    old_mechanic.is_available = True

        # 🔄 UPDATE NEW MECHANIC AVAILABILITY
        if new_mechanic:
            if new_status == "Completed":
                new_mechanic.is_available = True
            else:
                new_mechanic.is_available = False

        # 🔄 UPDATE SERVICE FIELDS
        service.status = new_status
        service.assigned_mechanic_id = new_mechanic_id

        db.session.commit()

        flash("Service updated successfully", "success")
        return redirect(url_for("ui.services_list"))

    return render_template(
        "services/update.html",
        service=service,
        vehicles=vehicles,
        mechanics=mechanics
    )


@ui.route("/services/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def services_delete(id):
    service = ServiceRequest.query.get(id)

    if not service:
        flash("Service request not found", "danger")
        return redirect(url_for("ui.services_list"))

    try:
        db.session.delete(service)
        db.session.commit()
        flash("Service request deleted successfully", "success")

    except IntegrityError:
        db.session.rollback()
        flash(
            "Cannot delete service request because an invoice exists for this service",
            "danger"
        )

    except Exception as e:
        db.session.rollback()
        flash("Failed to delete service request", "danger")

    return redirect(url_for("ui.services_list"))


# ---------- Mechanics ----------
@ui.route("/mechanics")
@login_required
@role_required("admin")
def mechanics_list():
    mechanics = Mechanic.query.all()
    return render_template("mechanics/list.html", mechanics=mechanics)


@ui.route("/mechanics/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def mechanics_create():
    if request.method == "POST":
        phone = request.form["phone"]

        # PRE-CHECK: Duplicate phone number
        existing_mechanic = Mechanic.query.filter_by(phone=phone).first()
        if existing_mechanic:
            flash(
                "Mechanic with this phone number already exists",
                "danger"
            )
            return redirect(url_for("ui.mechanics_create"))
        
        mechanic = Mechanic(
            name=request.form["name"],
            phone=request.form["phone"],
            specialization=request.form.get("specialization"),
            is_available=True if request.form.get("is_available") else False
        )
        try:
            db.session.add(mechanic)
            db.session.commit()
            flash("Mechanic added successfully", "success")
            return redirect(url_for("ui.mechanics_list"))
        except IntegrityError:
            db.session.rollback()
            flash(
                "Mechanic phone number already exists",
                "danger"
            )
            return redirect(url_for("ui.mechanics_create"))
        
    return render_template("mechanics/create.html")

@ui.route("/mechanics/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def mechanics_update(id):
    mechanic = Mechanic.query.get_or_404(id)

    if request.method == "POST":
        mechanic.name = request.form["name"]
        mechanic.phone = request.form["phone"]
        mechanic.specialization = request.form.get("specialization")
        mechanic.is_available = True if request.form.get("is_available") else False

        db.session.commit()
        flash("Mechanic updated successfully", "success")
        return redirect(url_for("ui.mechanics_list"))

    return render_template("mechanics/update.html", mechanic=mechanic)

@ui.route("/mechanics/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def mechanics_delete(id):
    mechanic = Mechanic.query.get_or_404(id)

    db.session.delete(mechanic)
    db.session.commit()

    flash("Mechanic deleted successfully", "success")
    return redirect(url_for("ui.mechanics_list"))

# ---------- Invoices ----------
@ui.route("/invoices")
@login_required
@role_required("admin")
def invoices_list():
    invoices = Invoice.query.all()
    return render_template("invoices/list.html", invoices=invoices)

@ui.route("/invoices/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def invoices_create():
    services = ServiceRequest.query.filter_by(status="Completed").all()

    if request.method == "POST":
        invoice = Invoice(
            service_id=request.form["service_id"],
            customer_id=request.form["customer_id"],
            vehicle_id=request.form["vehicle_id"],
            total_amount=request.form["total_amount"],
            payment_status=request.form.get("payment_status", "Pending")
        )
        db.session.add(invoice)
        db.session.commit()
        return redirect(url_for("ui.invoices_list"))

    return render_template("invoices/create.html", services=services)

@ui.route("/invoices/<int:id>/update", methods=["GET", "POST"])
@login_required
@role_required("admin")
def invoices_update(id):
    invoice = Invoice.query.get_or_404(id)

    if request.method == "POST":
        invoice.payment_status = request.form["payment_status"]
        db.session.commit()

        flash("Invoice updated successfully", "success")
        return redirect(url_for("ui.invoices_list"))

    return render_template("invoices/update.html", invoice=invoice)

@ui.route("/invoices/<int:id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def invoices_delete(id):
    invoice = Invoice.query.get_or_404(id)

    db.session.delete(invoice)
    db.session.commit()

    flash("Invoice deleted successfully", "success")
    return redirect(url_for("ui.invoices_list"))
