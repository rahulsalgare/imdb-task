from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///imdb.sqlite"
    db.init_app(app)

    SWAGGER_URL = '/api/docs'
    API_URL = 'api-docs'

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'IMDB'
        }
    )
    from .movies import movie_blueprint
    from .users import user_blueprint

    app.register_blueprint(movie_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(swagger_ui_blueprint)

    return app
