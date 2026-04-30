from . import db
from sqlalchemy import DateTime
from datetime import datetime


class User_Book(db.Model):
    user_book_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    Book_id = db.Column(db.Integer, db.ForeignKey('book.Book_id'))
    Section_id = db.Column(db.Integer)
    Status = db.Column(db.String, default = "Pending")
    feedback = db.Column(db.String(10000), default = "None")

    expiration_period = db.Column(db.String(20))  


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.String(150), unique = True, nullable = False)
    firstName = db.Column(db.String(150), nullable = False)
    password = db.Column(db.String(150), nullable = False)
    count_access = db.Column(db.Integer, default = 0)

    books = db.relationship('User_Book', cascade='all, delete-orphan', backref='users')

    
class Section(db.Model):
    Section_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    Section_Title = db.Column(db.String(10000), unique = True, nullable = False)
    Section_Date = db.Column(db.String(20))  
    Section_Descript = db.Column(db.String(10000), nullable = False)

    books = db.relationship('Book', cascade='all, delete-orphan', backref='section')

class Book(db.Model):
    Book_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    Book_Name = db.Column(db.String(10000), nullable = False)
    Author = db.Column(db.String(10000), nullable = False)
    Synopsis = db.Column(db.String(10000), nullable = False)
    Content = db.Column(db.String(10000), nullable = False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.Section_id'), nullable = False)

    users = db.relationship('User_Book', cascade='all, delete-orphan', backref='books')

    feedback = db.relationship('User_Book', backref='book')

