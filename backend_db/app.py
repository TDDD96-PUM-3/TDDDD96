"""Flask application factory and extension/bootstrap wiring."""

from flask import Flask
from flask_cors import CORS
from config import config
from extensions import db, jwt, bcrypt
from routes import auth_bp, data_bp, backend_bp
import os


def create_app(env=None):
    """Create and configure the Flask application instance.

    Args:
        env: Optional environment key used to select configuration.
             Falls back to the FLASK_ENV environment variable.

    Returns:
        A configured Flask app with extensions, JWT callbacks and blueprints.
    """
    app = Flask(__name__)

    # Ladda konfiguration
    env = env or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])

    # Koppla extensions till appen
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Enable CORS for frontend communication
    CORS(app, origins=["http://localhost:5173", "http://localhost:8000",
         "http://localhost:3000", "http://frontend:5173", "http://backend_db:8000"])

    # Importera JWT-callbacks så att de registreras på jwt-managern.
    # (Dekoratorerna körs först när modulen importeras.)
    from utils import token_check  # noqa: F401

    # Registrera blueprints (routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(backend_bp)

    # Skapa tabeller om de inte finns
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
