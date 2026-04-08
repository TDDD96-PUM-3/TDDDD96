import os

class Config:
    """ Baskonfiguration som delas av alla miljöer """
    JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """ Lokal utveckling – SQLite """
    DEBUG = True
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'

class ProductionConfig(Config):
    """ Produktion – PostgreSQL (t.ex. Azure) """
    DEBUG = False

    @staticmethod
    def get_db_uri():
        conn = os.environ.get('AZURE_POSTGRESQL_CONNECTIONSTRING', '')
        values = dict(x.split('=') for x in conn.split(' '))
        user     = values['user']
        host     = values['host']
        database = values['dbname']
        password = values['password']
        return f'postgresql+psycopg2://{user}:{password}@{host}/{database}'

    SQLALCHEMY_DATABASE_URI = get_db_uri.__func__()


# Välj konfiguration baserat på miljövariabel
config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}