from datetime import datetime

from flask import Blueprint, jsonify, request

from . import db
from .decorators import auth_required
from .models import Genre, Movie, Review

movie_blueprint = Blueprint('movies', __name__)


@movie_blueprint.route('/movies', methods=['GET'])
def view_movies():
    movie_list = Movie.query.all()
    movies = []

    for movie in movie_list:
        genre_list = movie.types
        movies.append(
            {'id': movie.id, 'name': movie.name, 'director': movie.director,
             'date_added': movie.date_created, 'imdb_score': movie.imdb_score,
             'number_of_votes': movie.no_of_votes, 'genres': [genre.name for genre in genre_list]}
        )

    return jsonify({'movies': movies})


@movie_blueprint.route('/movies/<movie_id>', methods=['GET'])
def view_one_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'No movie found'})

    movie = {
        'id': movie.id,
        'name': movie.name,
        'imdb_score': movie.imdb_score,
        'number_of_votes': movie.no_of_votes,
        'director': movie.director,
        'date_added': movie.date_created
    }

    return jsonify({'movie': movie})


@movie_blueprint.route('/movies/create', methods=['POST'])
@auth_required
def add_movies(current_user):
    # if not current_user.admin:
    #     return jsonify({'message': 'Unauthorized'}), 401

    movie_data = request.get_json()
    new_movie = Movie(name=movie_data['name'], director=movie_data['director'],
                      date_created=datetime.now())
    db.session.add(new_movie)
    try:
        for genre in movie_data['genres']:
            g = Genre.query.filter_by(name=genre).first()
            g.genres.append(new_movie)
    except:
        return jsonify({'message': 'genres not valid'}), 400
    db.session.commit()

    return jsonify({'message': 'Movie created'}), 201


@movie_blueprint.route('/movies/delete/<movie_id>', methods=['DELETE'])
@auth_required
def delete_movie(current_user, movie_id):
    # if not current_user.admin:
    #     return jsonify({'message': 'Unauthorized'}), 401

    movie = Movie.query.get(movie_id)
    movie.types = []
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie Deleted'}), 200


@movie_blueprint.route('/movies/update/<movie_id>', methods=['PATCH'])
@auth_required
def update_movie(current_user, movie_id):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid request'}), 400
    allowed_update_fields = {'name', 'director', 'genres'}
    if not set(data.keys()).issubset(allowed_update_fields):
        return jsonify({'message': 'Only name and director can be updated'}), 400
    movie = Movie.query.get(movie_id)
    for key in data:
        if key == 'name':
            movie.name = data[key]
        if key == 'director':
            movie.director = data[key]
        if key == 'genres':
            try:
                for genre in data['genres']:
                    movie.types = []
                    g = Genre.query.filter_by(name=genre).first()
                    g.genres.append(movie)
            except:
                return jsonify({'message': 'genres not valid'}), 400

    db.session.commit()
    return jsonify({'message': 'Movie updated successfully'}), 200


@movie_blueprint.route('/movies/review', methods=['POST'])
@auth_required
def review(current_user):
    review_data = request.get_json()
    new_review = Review(rating=review_data['rating'], movie_id=review_data['movie_id'],
                        user_id=current_user.id, comment=review_data['comment'],
                        date_created=datetime.now())
    db.session.add(new_review)
    movie = Movie.query.get(review_data['movie_id'])
    imdb_score = 0
    movie.imdb_score = round(
        ((imdb_score * movie.no_of_votes) + new_review.rating) / (movie.no_of_votes + 1), 1
    )
    movie.no_of_votes += 1
    db.session.commit()
    return jsonify({'message': 'Review created'}), 201


@movie_blueprint.route('/add_genre', methods=['POST'])
def add_genre():
    data = request.get_json()
    genre = Genre.query.filter_by(name=data['name']).first()
    if genre:
        return jsonify({'message': 'Genre already exists'})
    new_genre = Genre(name=data['name'])
    db.session.add(new_genre)
    db.session.commit()
    return jsonify({'message': 'Genre added'})
