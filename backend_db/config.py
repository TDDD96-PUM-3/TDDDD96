"""Runtime configuration classes for development and production."""

import os


class Config:
    """Base configuration shared across all environments."""
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Local development configuration backed by SQLite."""
    DEBUG = True
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'


class ProductionConfig(Config):
    """Production configuration backed by PostgreSQL."""
    DEBUG = False

    @staticmethod
    def _build_db_uri():
        conn = os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING', '')
        values = dict(x.split('=') for x in conn.split(' '))
        return (f"postgresql+psycopg2://{values['user']}:{values['password']}"
                f"@{values['host']}/{values['dbname']}")

    # URI is built lazily to avoid failing import-time in local dev.
    SQLALCHEMY_DATABASE_URI = None

    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = self._build_db_uri()


# Map environment name -> configuration class.
config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
