from flask import Blueprint, request,session
from models.user import User
from extensions import db
from utils.response import success_response
from utils.error_handlers import unauthorized, bad_request
from utils.validators import get_json_data

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")



@auth_bp.route("/register", methods=["POST"])
def register():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    user = User(
        username=data["username"],
        email=data["email"],
        role=data.get("role", "admin")
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return success_response(message= "User registered successfully",status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = get_json_data(request)
    if not data:
        return bad_request("JSON body required")

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        session["user_id"] = user.id
        return success_response(message= "Login successful")

    return unauthorized("Invalid credentials")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return success_response(message = "Logged out successfully")
