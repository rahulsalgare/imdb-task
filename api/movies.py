from datetime import datetime

from cerberus import Validator
from flask import Blueprint, jsonify, request

from . import db
from .decorators import auth_required
from .models import Genre, Movie, Review
from .schemas import movie_schema, genres_schema, review_schema

movie_blueprint = Blueprint('movies', __name__)

v = Validator()


@movie_blueprint.route('/movies', methods=['GET'])
def view_movies():
    qu = request.args
    genres = Genre.query.with_entities(Genre.name).all()
    genres = set(g[0] for g in genres)

    if 'sort' in qu:
        if qu['sort'] == 'recent':
            movie_list = Movie.query.order_by(Movie.date_created.desc()).all()
        elif qu['sort'] == 'popularity':
            movie_list = Movie.query.order_by(Movie.no_of_votes.desc()).all()
        elif qu['sort'] == 'imdb_score':
            movie_list = Movie.query.order_by(Movie.imdb_score.desc()).all()

    elif 'search' in qu:
        if qu['search'] in genres:
            g = Genre.query.filter_by(name=qu['search']).first()
            movie_list = g.genres.all()

        else:
            search_word = qu['search']
            movie_list = Movie.query.whooshee_search(search_word).all()

    else:
        movie_list = Movie.query.all()
    movies = []

    for movie in movie_list:
        genre_list = movie.types
        movies.append(
            {'id': movie.id, 'name': movie.name, 'director': movie.director,
             'date_added': movie.date_created, 'imdb_score': movie.imdb_score,
             'number_of_votes': movie.no_of_votes, 'genres': [genre.name for genre in genre_list]}
        )

    return jsonify({'movies': movies}), 200


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
        'date_added': movie.date_created,
        'genres': [genre.name for genre in movie.types]
    }

    return jsonify({'movie': movie})


@movie_blueprint.route('/movies/create', methods=['POST'])
@auth_required
def add_movies(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401

    movie_data = request.get_json()

    if not v(movie_data, movie_schema):
        return jsonify(v.errors)

    new_movie = Movie(name=movie_data['name'], director=movie_data['director'],
                      date_created=datetime.now())
    try:
        for genre in movie_data['genres']:
            g = Genre.query.filter_by(name=genre).first()
            g.genres.append(new_movie)
    except:
        return jsonify({'message': 'genres not valid'}), 400
    db.session.add(new_movie)
    db.session.commit()

    movie = {
        'id': new_movie.id,
        'name': new_movie.name,
        'imdb_score': new_movie.imdb_score,
        'number_of_votes': new_movie.no_of_votes,
        'director': new_movie.director,
        'date_added': new_movie.date_created
    }

    return jsonify({'movie': movie}), 201


@movie_blueprint.route('/movies/bulk/create', methods=['POST'])
@auth_required
def movies_bulk_create(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()

    for movie in data:
        if not v(movie, movie_schema):
            return jsonify(v.errors)
        new_movie = Movie(name=movie['name'], director=movie['director'],
                          date_created=datetime.now())
        try:
            for genre in movie['genres']:
                g = Genre.query.filter_by(name=genre).first()
                g.genres.append(new_movie)
        except:
            return jsonify({'message': f'genre {genre} not valid'}), 400

        db.session.add(new_movie)

    db.session.commit()
    return jsonify({'message': 'movies created'}), 201


@movie_blueprint.route('/movies/delete/<movie_id>', methods=['DELETE'])
@auth_required
def delete_movie(current_user, movie_id):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401

    movie = Movie.query.get(movie_id)
    movie.types = []
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': 'Movie Deleted'}), 204


@movie_blueprint.route('/movies/update/<movie_id>', methods=['PATCH'])
@auth_required
def update_movie(current_user, movie_id):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401

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
    movie = {
        'id': movie.id,
        'name': movie.name,
        'imdb_score': movie.imdb_score,
        'number_of_votes': movie.no_of_votes,
        'director': movie.director,
        'date_added': movie.date_created
    }
    return jsonify({'movie': movie}), 200


@movie_blueprint.route('/movies/review', methods=['POST'])
@auth_required
def review(current_user):
    review_data = request.get_json()
    if not v(review_data, review_schema):
        return jsonify(v.errors)
    check_review = Review.query.filter_by(movie_id=review_data['movie_id'], user_id=current_user.id).first()
    if check_review:
        return jsonify({'message': 'Review already exists'})
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


@movie_blueprint.route('/add_genres', methods=['POST'])
@auth_required
def add_genre(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()

    if not v(data, genres_schema):
        return jsonify(v.errors)

    for genre in data['genres']:
        genre_check = Genre.query.filter_by(name=genre).first()
        if genre_check:
            return jsonify({'message': 'Genre already exists'}), 400

        new_genre = Genre(name=genre)
        db.session.add(new_genre)

    db.session.commit()
    return jsonify({'message': 'Genres added'}), 201
