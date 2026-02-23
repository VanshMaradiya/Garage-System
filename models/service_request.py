from extensions  import db
from datetime import datetime

class ServiceRequest(db.Model):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)

    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False
    )

    service_type = db.Column(db.String(100), nullable=False)

    service_date = db.Column(
        db.Date,
        nullable=False
    )

    problem_description = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        
        db.String(20),
        nullable=False,
        default="Pending"   # Pending | In Progress | Completed
    )

    assigned_mechanic_id = db.Column(
        db.Integer,
        db.ForeignKey("mechanics.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    vehicle = db.relationship("Vehicle")
    mechanic = db.relationship("Mechanic")

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('Pending', 'In Progress', 'Completed')",
            name="check_service_status"
        ),
    )
    
    # REPRESENTATION (for debugging/logs)
    def __repr__(self):
         return (
            f"<ServiceRequest id={self.id} "
            f"vehicle_id={self.vehicle_id} status={self.status}>"
    )







