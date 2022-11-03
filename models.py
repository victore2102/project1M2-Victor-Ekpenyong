'''Database Models'''
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Members(db.Model):
    '''Database'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)


def __repr__(self):
        return '<Members %r>' % self.username

