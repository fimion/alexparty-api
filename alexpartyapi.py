import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
app.config.from_pyfile('.env')

db = SQLAlchemy(app)


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


@app.route('/')
def hello_world():
    return jsonify('Hello World!')


@app.route('/posts')
def get_posts():
    return jsonify(Post.page())

if __name__ == '__main__':
    app.run()
