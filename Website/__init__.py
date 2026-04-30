from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_restful import Api


db =  SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bottle'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    from .api import SectionAPI, BookAPI
    
    api.add_resource(SectionAPI, '/addSection', '/editSection/<int:section_id>')
    api.add_resource(BookAPI, '/<int:section_id>/book')
   
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    from .models import User
    from .models import Section
    from .models import Book
    from .models import User_Book
   
    with app.app_context():
        db.create_all()
   
    return app
