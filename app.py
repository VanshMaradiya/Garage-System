from flask import Flask
from config import Config
from extensions import db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 🔴 REGISTER BLUEPRINTS
    from routes.auth_routes import auth_bp
    from routes.customer_routes import customer_bp
    from routes.service_routes import service_bp
    from routes.vehicle_routes import vehicle_bp
    from routes.invoice_routes import invoice_bp
    from routes.mechanic_routes import mechanic_bp
    from routes.ui_routes import ui

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(mechanic_bp)
    app.register_blueprint(ui)


    return app

app = create_app()
app.secret_key = "dev-secret-key"

if __name__ == "__main__":
    app.run(debug=True)



