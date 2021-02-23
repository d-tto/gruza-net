from flask import Flask, request, jsonify, make_response, abort, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
db_path = os.path.join(os.path.dirname(__file__), 'api.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)

cors = CORS(app)
db = SQLAlchemy(app)


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    followed = db.relationship('User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            db.session.add(self)
            db.session.commit()
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            db.session.add(self)
            db.session.commit()
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_list(self):
        return self.followed.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {
            'public_id': self.public_id,
            'username': self.username,
            'email': self.email,
        }

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address

    def __repr__(self):
        return '<User %r>' % self.username


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response('Токен недействителен или отсутствует', 401)

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user_current = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return make_response('Токен недействителен или отсутствует', 401)

        return f(user_current, *args, **kwargs)

    return decorated


@app.route('/create', methods=['POST'])
def user_create():
    data = request.get_json()

    if not data:
        return make_response('Ошибка параметров', 500)

    try:
        hashed_password = generate_password_hash(data['password'], method='sha256')
        user_new = User(public_id=str(uuid.uuid4()), email=data['email'],
                        username=data['username'], password=hashed_password)
        user_new.save()
    except:
        return make_response('Ошибка параметров', 500)

    return jsonify({'message': 'Пользователь создан'})


@app.route('/update/<public_id>', methods=['PUT'])
@token_required
def user_update(user_current, public_id):
    data = request.get_json()

    if not data:
        return make_response('Ошибка параметров', 500)

    user = User.query.filter_by(public_id=public_id).first()

    if not user or not user_current == user:
        return make_response('Ошибка доступа', 500)

    if data['password'].strip():
        data['password'] = generate_password_hash(data['password'], method='sha256')

    try:
        for key, value in data.items():
            if hasattr(user, key) and (key in ['username', 'password']):
                if value:
                    setattr(user, key, value)
    except:
        return make_response('Неверный формат параметра', 500)

    user.save()

    return jsonify({'public_id': user.public_id, 'username': user.username})


@app.route('/auth')
def auth():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Ошибка аутентификации', 401, {'WWW-Authenticate': 'Basic realm="Authentication error"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Ошибка аутентификации', 401, {'WWW-Authenticate': 'Basic realm="Authentication error"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('utf-8'), 'public_id': user.public_id, 'username': user.username})

    return make_response('Ошибка аутентификации', 401, {'WWW-Authenticate': 'Basic realm="Authentication error"'})


@app.route('/get/<public_id>', methods=['GET'])
@token_required
def user_profile(user_current, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user or not user_current == user:
        return make_response('Ошибка доступа', 500)

    followed = user.followed_list()
    output = []
    for f in followed:
        f_json = f.json()
        output.append({'public_id': f_json['public_id'], 'username': f_json['username']})

    user_data = user.json()
    user_data['followed'] = output

    return jsonify({'user': user_data})


@app.route('/delete/<public_id>', methods=['DELETE'])
@token_required
def user_delete(user_current, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user or not user_current == user:
        return make_response('Ошибка доступа', 500)

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Пользователь удален'})


@app.route('/list/<int:page>', methods=['GET'])
def users_list(page):
    users = User.query.order_by(User.id.desc()).paginate(page, 5, error_out=False)
    output = []

    for user in users.items:
        output.append(user.json())

    return jsonify({'users': output, 'pages': users.pages})


@app.route('/follow/<public_id>', methods=['POST'])
@token_required
def follow(user_current, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user or user_current == user:
        return make_response('Ошибка доступа', 500)

    user_current.follow(user)

    return jsonify({'message': 'Пользователь добавлен в подписки'})


@app.route('/unfollow/<public_id>', methods=['POST'])
@token_required
def unfollow(user_current, public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user or user_current == user:
        return make_response('Ошибка доступа', 500)

    user_current.unfollow(user)

    return jsonify({'message': 'Пользователь удален из подписок'})


if __name__ == '__main__':
    app.run()
