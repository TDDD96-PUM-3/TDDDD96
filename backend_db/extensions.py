from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Initialized here and bound to the app in app.py via init_app().
# Import these instances in models/routes; do not create new ones per module.
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
