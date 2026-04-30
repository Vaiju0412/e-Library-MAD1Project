from flask_restful import Resource, reqparse, abort, fields, marshal_with
from flask import redirect, render_template, request, flash, url_for
from .models import Section, Book
from . import db
from datetime import datetime

section_args = reqparse.RequestParser()
section_args.add_argument('Section_Title', location = 'form', type=str)
section_args.add_argument('Section_Date', location = 'form', type=str)
section_args.add_argument('Section_Descript', location = 'form', type=str)

book_args = reqparse.RequestParser()
book_args.add_argument('Book_Name', location = 'form', type=str)
book_args.add_argument('Author', location = 'form', type=str)
book_args.add_argument('Content', location = 'form', type=str)
book_args.add_argument('Synopsis', location = 'form', type=str)




section_fields = {
	'Section_Title': fields.String,
	'Section_Date': fields.String,
	'Section_Descript': fields.String
}

book_fields = {
	'Book_Name': fields.String,
	'Author': fields.String,
	'Content': fields.String,
    'Synopsis': fields.String

}

class SectionAPI(Resource):
    def post(self):              
        args = section_args.parse_args()
        title = Section.query.filter_by(Section_Title = args['Section_Title']).first()
              
        if title:
            flash('Section already exists!', category = 'error')
            return redirect('/home')
                
        new_section = Section(Section_Title=args['Section_Title'], Section_Date = datetime.now().strftime("%dth %b, %Y"), Section_Descript=args['Section_Descript'])
        db.session.add(new_section)
        db.session.commit()
        flash('Section created successfully', category = 'success')


        return redirect('/home')
        
class BookAPI(Resource):
    def post(self,section_id):              
        args = book_args.parse_args()
        name = Book.query.filter_by(Book_Name = args['Book_Name']).first()
        
        if name:
            flash('Book already exists!', category = 'error')
            return redirect('/home')
                
        new_book =  Book(Book_Name=args['Book_Name'], Author=args['Author'], Content=args['Content'], Synopsis = args['Synopsis'], section_id = section_id)

        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully', category = 'success')


        return redirect('/home')       
