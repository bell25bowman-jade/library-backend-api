from flask import Flask
from .models import db
from .blueprints.members import members_bp
from .blueprints.book import book_bp
from .blueprints.loan import loan_bp
from .extensions import ma, limiter, cache
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Your API's Name"
    }
)


def create_app(config_name: str):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    #register blueprints
    app.register_blueprint(members_bp, url_prefix="/members")
    app.register_blueprint(book_bp, url_prefix="/books")
    app.register_blueprint(loan_bp, url_prefix="/loans")
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    
    return app
