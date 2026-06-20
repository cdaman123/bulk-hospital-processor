from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from flask_smorest import Api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    api = Api(app)

    from app.api.routes import bp as api_bp
    api.register_blueprint(api_bp)

    return app
