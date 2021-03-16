import datetime
import uuid

import jwt
from flask import Blueprint, current_app, jsonify, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User
from .schemas import user_schema
from cerberus import Validator
from .decorators import auth_required

v = Validator()
user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if not v(user_data, user_schema):
        return jsonify(v.errors)
    hashed_password = generate_password_hash(user_data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()), name=user_data['name'], password=hashed_password,
                    admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'}), 201


@user_blueprint.route('/get_users', methods=['GET'])
@auth_required
def get_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401
    user_list = User.query.all()
    users = []

    for user in user_list:
        users.append({
            'public_id': user.public_id,
            'name': user.name,
            'password': user.password,
            'admin': user.admin
        })

    return jsonify({'users': users})


@user_blueprint.route('/get_user/<public_id>', methods=['GET'])
@auth_required
def get_one_user(current_user,public_id):
    if not current_user.admin:
        return jsonify({'message': 'Unauthorized'}), 401
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found'})

    user = {
        'public_id': user.public_id,
        'name': user.name,
        'password': user.password,
        'admin': user.admin
    }

    return jsonify({'user': user})


@user_blueprint.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401,
                             {'WWW-Authenticate': 'Basic realm="Login required"'})

    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401,
                             {'WWW-Authenticate': 'Basic realm="Login required"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.public_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            current_app.config['SECRET_KEY']
        )

        return jsonify({'token': token})

    return make_response('Could not verify', 401,
                         {'WWW-Authenticate': 'Basic realm="Login required"'})
