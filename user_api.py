import flask
from flask import jsonify, request
from data import db_session
from data.users import User


blueprint = flask.Blueprint('user_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/user')
def get_user():
    session = db_session.create_session()
    user = session.query(User).all()
    return jsonify({'user': [item.to_dict(only=('surname', 'name',
                                                'age', 'position', 'city_from',
                                                'speciality', 'address', 'email'))
                             for item in user]})


@blueprint.route('/api/user/<int:user_id>',  methods=['GET'])
def get_one_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify({'user': user.to_dict(only=('surname', 'name',
                                               'age', 'position', 'city_from',
                                               'speciality', 'address', 'email'))})


@blueprint.route('/api/user', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['id', 'surname', 'name', 'age', 'position', 'speciality', 'address', 'email', 'city_from']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = session.query(User).filter(User.id == request.json['id']).first()
    if not user:
        user = User()
        user.surname = request.json['surname']
        user.id = request.json['id']
        user.name = request.json['name']
        user.age = request.json['age']
        user.position = request.json['position']
        user.speciality = request.json['speciality']
        user.address = request.json['address']
        user.email = request.json['email']
        user.city_from = request.json['city_from']
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
    else:
        return jsonify({'error': 'Id already exists'})


@blueprint.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = db_session.create_session()
    print(session.query(User).all())
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/user', methods=['PUT'])
def edit_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif 'id' not in request.json:
        return jsonify({'error': 'There is no ID'})
    session = db_session.create_session()
    user = session.query(User).filter(User.id == request.json['id']).first()
    if user:
        user.surname = request.json.get('surname', user.surname)
        user.name = request.json.get('name', user.name)
        user.age = request.json.get('age', user.age)
        user.position = request.json.get('position', user.position)
        user.speciality = request.json.get('speciality', user.speciality)
        user.address = request.json.get('address', user.address)
        user.email = request.json.get('email', user.email)
        user.city_from = request.json.get('city_from', user.city_from)
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
    else:
        return jsonify({'error': 'There is no user with the id'})

