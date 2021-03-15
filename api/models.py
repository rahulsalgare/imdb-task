from . import db

genres = db.Table(
    'genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    imdb_score = db.Column(db.Float, nullable=True)
    director = db.Column(db.String(50))
    date_created = db.Column(db.DateTime)
    no_of_votes = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='movie', lazy=True)
    types = db.relationship('Genre', secondary=genres,
                            backref=db.backref('genres', lazy='dynamic'))


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Integer)
    reviews = db.relationship('Review', backref='user', lazy=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    date_created = db.Column(db.DateTime)
