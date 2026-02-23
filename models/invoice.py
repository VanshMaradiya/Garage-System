from extensions import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("service_requests.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("vehicles.id"),
        nullable=False
    )

    total_amount = db.Column(db.Float, nullable=False)

    payment_status = db.Column(db.String(20), default="Pending")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship("ServiceRequest")
    customer = db.relationship("Customer")
    vehicle = db.relationship("Vehicle")
    
    # REPRESENTATION (for debugging/logs)
    def __repr__(self):
        return f"<Invoice id={self.id} amount={self.amount}>"
