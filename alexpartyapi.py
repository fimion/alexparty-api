import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
    RoleMixin, auth_token_required, login_required, current_user

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_pyfile('.env')

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Post(db.Model):
    """Our Post Model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def page(number=10, offset=0):
        p = Post.query.order_by(desc(Post.date)).limit(number).offset(offset)
        result = [i.serialize for i in p.all()]
        return result

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': int(self.date.timestamp()*1000)
        }

    def __repr__(self):
        return "Post: {} - {}".format(self.id, self.title)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
# @app.before_first_request
# def create_user():
#     db.create_all()
#     user_datastore.create_user(username='fimion', email='fimion@gmail.com', password='password')
#     db.session.commit()


@app.route('/')
def hello_world():
    return jsonify('Hello World!')


@app.route('/posts')
def get_posts():
    return jsonify(Post.page())


@app.route('/_/posts/<id>', methods=['POST', 'PUT', 'DELETE'])
@auth_token_required
def edit_posts(id):
    return jsonify(request.form)


@app.route('/_/token', methods=['GET'])
@login_required
def get_token():
    return jsonify(current_user.get_auth_token())

if __name__ == '__main__':
    app.run()
