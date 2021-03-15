from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '3d6f45a5fc12445dbac2f59c3b6c7cb1'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///imdb.sqlite"
    db.init_app(app)

    from .movies import movie_blueprint
    from .users import user_blueprint
    from .models import Movie

    app.register_blueprint(movie_blueprint)
    app.register_blueprint(user_blueprint)

    return app
