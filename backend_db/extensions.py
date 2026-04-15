from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Initieras här, kopplas till appen i app.py via init_app()
# Importera dessa instanser i modeller och routes – aldrig skapa nya
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()