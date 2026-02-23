from extensions import db
from datetime import datetime
from models.customer import Customer


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False
    )

    vehicle_number = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )

    vehicle_type = db.Column(
        db.String(50),
        nullable=False
    )

    brand = db.Column(
        db.String(50),
        nullable=False
    )

    model = db.Column(
        db.String(50),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customer = db.relationship("Customer", backref="vehicles")

    # # relationship
    # services = db.relationship(
    #     "ServiceRequest",
    #     backref="vehicle",
    #     lazy=True,
    #     cascade="all, delete"
    # )

    # REPRESENTATION (for debugging/logs)
    def __repr__(self):
        return f"<Vehicle id={self.id} number={self.vehicle_number}>"