import os
import sqlalchemy as sa
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(100), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False, default='image/jpeg')
    md5_hash = db.Column(db.String(100), nullable=False, default='')
    storage_filename = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(100))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100), nullable=False, default='')
    first_name = db.Column(db.String(100), nullable=False, default='')
    middle_name = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text, nullable=False, default='')
    full_desc = db.Column(db.Text, nullable=False, default='')
    rating_sum = db.Column(db.Integer, nullable=False, default=0)
    rating_num = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    background_image_id = db.Column(db.String(100), db.ForeignKey('images.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    category = db.relationship('Category')
    author = db.relationship('User')
    bg_image = db.relationship('Image')
    reviews = db.relationship('Review', backref='course', lazy='dynamic',
                              order_by='Review.created_at.desc()')

    @property
    def rating(self):
        if self.rating_num == 0:
            return 0
        return self.rating_sum / self.rating_num

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
