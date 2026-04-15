from flask import Flask, jsonify, request
from config import config
from extensions import db, jwt, bcrypt
from routes import auth_bp, data_bp, backend_bp
import os


def create_app(env=None):
    """ Application factory – skapar och konfigurerar Flask-appen """
    app = Flask(__name__)

    # Ladda konfiguration
    env = env or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[env])

    # Koppla extensions till appen
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

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
