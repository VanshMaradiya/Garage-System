from datetime import datetime
from extensions import db

class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20),unique=True, nullable=False)
    email = db.Column(db.String(150))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # REPRESENTATION (for debugging/logs)
    def __repr__(self):
        return f"<Customer id={self.id} name={self.name}>"


