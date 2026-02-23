from extensions import db
from datetime import datetime

class Mechanic(db.Model):
    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False)
    
    phone = db.Column(db.String(15), unique=True, nullable=False)
    
    specialization = db.Column(db.String(100))
    
    is_available = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # REPRESENTATION (for debugging/logs)
    def __repr__(self):
        return f"<Mechanic id={self.id} name={self.name}>"
