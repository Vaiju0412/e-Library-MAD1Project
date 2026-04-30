from flask import Blueprint, render_template, flash, request, redirect
from .models import Section, Book, User, User_Book
from . import db
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt



views = Blueprint('views',__name__)

BASE = 'http://127.0.0.1:5000'

@views.route('/home', methods = ['GET', 'POST'])
def home():
    
    sections = Section.query.all()
    books = Book.query.all()

    return render_template('home.html', sections = sections, book = books)



@views.route('/<string:role>/<int:id>/search', methods =['GET', 'POST'])
def search(role,id):
   if request.method == "POST":
      query = request.form.get('search')
      selected_filter = request.form.get('filter')

      if role == "user":
         user = User.query.filter_by(id = id).first()
         
         matching_books = Book.query.filter(Book.Book_Name.ilike(f'%{query}%')).filter(Book.Book_Name.contains(f'{query}')).all()
         matching_authors = Book.query.filter(Book.Author.ilike(f'%{query}%')).filter(Book.Author.contains(f'{query}')).all()
         matching_sections = Section.query.filter(Section.Section_Title.ilike(f'%{query}%')).filter(Section.Section_Title.contains(f'{query}')).all()

         requested_books = User_Book.query.filter_by(User_id = id, Status = "Pending").all()
         requested_book_ids = [book.Book_id for book in requested_books]

         issued_books = User_Book.query.filter_by(User_id = id, Status = "Issued").all()
         issued_book_ids = [book.Book_id for book in issued_books]

         rejected_books = User_Book.query.filter_by(User_id = id, Status = "Rejected").all()         
         rejected_book_ids = [book.Book_id for book in rejected_books]

         if matching_books and selected_filter == 'books':
               
               matching_requested_books = [book for book in matching_books if book.Book_id in requested_book_ids]
               matching_issued_books = [book for book in matching_books if book.Book_id in issued_book_ids]
               matching_rejected_books = [book for book in matching_books if book.Book_id in rejected_book_ids]

               matching_available_books = [book for book in matching_books if (book.Book_id not in requested_book_ids and book.Book_id not in issued_book_ids and book.Book_id not in rejected_book_ids)]

               return render_template('user_search.html', user = user, available_books = matching_available_books, requested_books = matching_requested_books, issued_books = matching_issued_books, rejected_books = matching_rejected_books)
         
         elif matching_authors and selected_filter == 'authors':

            matching_requested_authors = [book for book in matching_authors if book.Book_id in requested_book_ids]
            matching_issued_authors = [book for book in matching_authors if book.Book_id in issued_book_ids]
            matching_rejected_authors = [book for book in matching_authors if book.Book_id in rejected_book_ids]

            matching_available_authors = [book for book in matching_authors if (book.Book_id not in requested_book_ids and book.Book_id not in issued_book_ids and book.Book_id not in rejected_book_ids)]

            return render_template('user_search.html', user = user, available_authors = matching_available_authors, requested_authors = matching_requested_authors, issued_authors = matching_issued_authors, rejected_authors = matching_rejected_authors)
            
         elif matching_sections and selected_filter == 'sections':

            matching_section_books = {}

            for section in matching_sections:

               section_books = section.books

               section_requested_books = [book for book in section_books if book.Book_id in requested_book_ids]
               section_issued_books = [book for book in section_books if book.Book_id in issued_book_ids]
               section_rejected_books = [book for book in section_books if book.Book_id in rejected_book_ids]
               section_available_books = [book for book in section_books if (book.Book_id not in requested_book_ids and book.Book_id not in issued_book_ids and book.Book_id not in rejected_book_ids)]

               matching_section_books[section.Section_Title] = { 'requested_books': section_requested_books, 'issued_books': section_issued_books,'rejected_books': section_rejected_books, 'available_books': section_available_books}

               return render_template('user_search.html', user = user, matching_section_books = matching_section_books)   
                           
         else:
            flash("Sorry! requested search could not be found", category = "error")
            return redirect(f'/{id}/dashboard')
      
      else:
         matching_books = Book.query.filter(Book.Book_Name.ilike(f'%{query}%')).filter(Book.Book_Name.contains(f'{query}')).all()
         matching_authors = Book.query.filter(Book.Author.ilike(f'%{query}%'))
         matching_sections = Section.query.filter(Section.Section_Title.ilike(f'%{query}%')).filter(Section.Section_Title.contains(f'{query}')).all()

         if matching_books and selected_filter == 'books':
            matching_users_books = {}

            for book in matching_books:
               users_books = User_Book.query.filter_by(Book_id=book.Book_id).all()

               matching_requested_books = [user_book for user_book in users_books if user_book.Status == 'Pending']
               matching_issued_books = [user_book for user_book in users_books if user_book.Status in ['Returned', 'Issued']]
               matching_rejected_books = [user_book for user_book in users_books if user_book.Status == 'Rejected']

               matching_users_books[book.Book_id] = {
                  'requested_books': matching_requested_books,
                  'issued_books': matching_issued_books,
                  'rejected_books': matching_rejected_books
               }

            requested_book_ids = [user_book.Book_id for user_book in matching_requested_books]
            issued_book_ids = [user_book.Book_id for user_book in matching_issued_books]
            rejected_book_ids = [user_book.Book_id for user_book in matching_rejected_books]
            matching_available_books = [book for book in matching_books if (book.Book_id not in requested_book_ids and book.Book_id not in issued_book_ids and book.Book_id not in rejected_book_ids)]

            matching_users_books['available_books'] = matching_available_books

            return render_template('lib_search.html', matching_users_books=matching_users_books)
         
         if matching_sections and selected_filter == 'sections':
               
            return render_template('lib_search.html', matching_sections = matching_sections)
         
         if matching_authors and selected_filter == 'authors':
            matching_authors_books = {}

            for author in matching_authors:

               requested_books = []
               issued_books = []
               rejected_books = []

               user_books = User_Book.query.filter_by(Book_id=author.Book_id).all()

               matching_requested_books = [user_book for user_book in user_books if user_book.Status == 'Pending']
               matching_issued_books = [user_book for user_book in user_books if user_book.Status in ['Returned', 'Issued']]
               matching_rejected_books = [user_book for user_book in user_books if user_book.Status == 'Rejected']

               requested_books.extend(matching_requested_books)
               issued_books.extend(matching_issued_books)
               rejected_books.extend(matching_rejected_books)

               matching_authors_books[author] = {
                     'requested_books': requested_books,
                     'issued_books': issued_books,
                     'rejected_books': rejected_books
               }

               requested_book_ids = [user_book.Book_id for user_book in matching_requested_books]
               issued_book_ids = [user_book.Book_id for user_book in matching_issued_books]
               rejected_book_ids = [user_book.Book_id for user_book in matching_rejected_books]
               matching_available_books = [book for book in matching_authors if (book.Book_id not in requested_book_ids and book.Book_id not in issued_book_ids and book.Book_id not in rejected_book_ids)]

               matching_authors_books['available_books'] = matching_available_books

            return render_template('lib_search.html', matching_authors_books=matching_authors_books)

         
         else:
            flash("Sorry! requested search could not be found", category = "error")
            return redirect('/home')               

@views.route('/addSection', methods = ['GET', 'POST'])
def addSection(): 

   data = request.form
   requests.post(BASE + '/addSection', data = data)

@views.route('/<int:section_id>/editSection', methods = ['GET', 'POST'])
def editSection(section_id): 

   Title = request.form.get('Section_Title')

   title = Section.query.filter_by(Section_Title = Title).first()
              
   if title and title.Section_id != section_id:
      flash('Section already exists!', category = 'error')
      return redirect('/home')
        
   Descript = request.form.get('Section_Descript')

   section = Section.query.filter_by(Section_id = section_id).first()

   section.Section_Title = Title
   section.Section_Descript= Descript

   db.session.commit()
   flash('Section edited successfully', category = 'success')


   return redirect('/home') 


@views.route('/<int:section_id>/deleteSection', methods = ['GET', 'POST'])
def deleteSection(section_id): 

   section = Section.query.filter_by(Section_id = section_id).first()

   if section.books:
      flash("Please delete the books in this section first!!", category = "error")
      return redirect('/home')

   db.session.delete(section)
   db.session.commit()
   flash("Section deleted successfully!", category = "success")

   return redirect('/home')

@views.route('/<int:section_id>/book', methods = ['GET', 'POST'])
def addBook():

   data = request.form
   response = requests.post(BASE + '/{section_id}/book', data = data)


@views.route('/<int:section_id>/<int:book_id>/editBook', methods = ['GET', 'POST'])
def editBook(section_id,book_id):
   if request.method == "POST":

      Name = request.form.get('Book_Name')

      book = Book.query.filter_by(Book_Name = Name).first()

      if book:
         if book.Book_Name == Name and book.Book_id != book_id:         

            flash('Book already exists!', category = 'error')
            return redirect('/home')
         
      book = Book.query.filter_by(Book_id = book_id).first()   

      book.Book_Name = Name
      book.Author = request.form.get('Author')
      book.Synopsis = request.form.get('Synopsis')
      book.Content = request.form.get('Content')
         
      db.session.commit()
      flash('Book edited successfully', category = 'success')

      return redirect('/home')
      

@views.route('/<int:book_id>/deleteBook', methods = ['GET', 'POST'])
def deleteBook(book_id): 

   book = Book.query.filter_by(Book_id = book_id).first()

   db.session.delete(book)
   db.session.commit()
   flash("Book deleted successfully!", category = "success")

   return redirect('/home')


@views.route('/<int:id>/dashboard', methods = ['GET', 'POST'])
def user_home(id):

   user = User.query.filter_by(id = id).first()
   requested_books = User_Book.query.filter_by(User_id = id).all()
   returned_books = User_Book.query.filter_by(User_id = id, Status = "Returned").all()
   rejected_books = User_Book.query.filter_by(User_id = id, Status = "Rejected").all()
   all_returned_books = User_Book.query.filter_by(Status = "Returned").all()

   books = Book.query.all()

   requested_book_ids = [book.Book_id for book in requested_books]
   returned_book_ids = [book.Book_id for book in returned_books]
   rejected_book_ids = [book.Book_id for book in rejected_books]


   available_books = [book for book in books if (book.Book_id not in requested_book_ids) or (book.Book_id in rejected_book_ids)]
   returned_books = [book for book in books if book.Book_id in returned_book_ids]
   print(returned_books)
   sections = Section.query.all()

   for section in sections:
      
      section.available_books = [book for book in section.books if book in available_books]

   book_feedback = {}

   for user_book in all_returned_books:
      book_id = user_book.Book_id
      user_id = user_book.users.firstName
      feedback = user_book.feedback
    
      if feedback != "" and feedback != "None":
         if book_id not in book_feedback:
            book_feedback[book_id] = {}
         book_feedback[book_id][user_id] = feedback 
   
   return render_template('User.html', user = user, returned_books = returned_books, sections = sections, book_feedback = book_feedback)


@views.route('/<int:id>/<int:book_id>/request', methods = ['GET', 'POST'])
def user_request(id,book_id):

   user = User.query.filter_by(id = id).first()
   duration = request.form.get('duration')
   duration_value = request.form.get('duration_value')
   current_date = datetime.now()


   if duration == 'hours':
      expiration_time = current_date + timedelta(hours=int(duration_value))
      
   elif duration == 'days':
      expiration_time = current_date + timedelta(days=int(duration_value))
      
   elif duration == 'weeks':
      expiration_time = current_date + timedelta(weeks=int(duration_value))

   else:
      flash("Invalid duration", category = "error")



   if user.count_access < 5 and user.count_access >= 0:

      user.count_access = user.count_access + 1
      book = Book.query.filter_by(Book_id = book_id).first()
      section = book.section
      new_user_book = User_Book(User_id = id, Book_id = book_id, Section_id = section.Section_id, expiration_period = expiration_time.strftime("%H:%M %dth %b, %Y "))
      db.session.add(new_user_book)     
      db.session.commit()
      flash(f'Request submitted successfully You can access {5-user.count_access} more books', category = "success")

      return redirect(f'/{id}/dashboard')
   
   else:

      flash("You have reached maximum limit of accessing books.", category = "error")

      return redirect(f'/{id}/dashboard')
   

   
@views.route('/<int:id>/myBooks', methods = ['GET', 'POST'])
def myBooks(id):

   user = User.query.filter_by(id = id).first()

   requested_books = User_Book.query.filter_by(User_id = id, Status = "Pending").all()
   issued_books = User_Book.query.filter_by(User_id = id, Status = "Issued").all()
   rejected_books = User_Book.query.filter_by(User_id = id, Status = "Rejected").all()

   
   return render_template('myBooks.html', user = user, requested_books = requested_books, issued_books = issued_books, rejected_books = rejected_books)



@views.route('/requests', methods = ['GET', 'POST'])
def request_book():
 
   requested_books = User_Book.query.filter_by(Status = "Pending").all()

   issued_books = User_Book.query.filter_by(Status = "Issued").all()

   rejected_books = User_Book.query.filter_by(Status = "Rejected").all()

   return render_template('requests.html', requested_books = requested_books, issued_books = issued_books, rejected_books = rejected_books)



@views.route('/<int:id>/<int:book_id>/<string:issue>', methods = ['GET', 'POST'])
def issue(id, book_id, issue):

   user_book = User_Book.query.filter_by(User_id = id,Book_id = book_id, Status = "Pending").first()

   if issue == "Grant":
      user_book.Status = "Issued"
   
   elif issue == "Reject":
      user_book.Status = "Rejected"
      user_book.expiration_period = ""
      user = User.query.filter_by(id = id).first()
      user.count_access = user.count_access - 1 

   db.session.commit()
   
   return redirect('/requests')


@views.route('/<int:id>/<int:book_id>/<string:role>/revoke', methods = ['GET', 'POST'])
def user_revoke(id, book_id, role):

   user_book = User_Book.query.filter_by(User_id = id,Book_id = book_id).first()

   db.session.delete(user_book)

   user = User.query.filter_by(id = id).first()
   user.count_access = user.count_access - 1
   db.session.commit()

   if role == "admin":
      flash("Successfully revoked", category = "success")
      return redirect('/requests')      
   else:      
      flash(f'Successfully revoked access. You can access {5 - user.count_access} more books. Keep Browsing!!', category = "success")
      return redirect(f'/{id}/dashboard')


@views.route('/<int:id>/<int:book_id>/return', methods = ['GET', 'POST'])
def return_book(id, book_id):

   user_book = User_Book.query.filter_by(User_id = id, Book_id = book_id, Status = "Issued").first()

   feedback = request.form.get('feedback')
   user_book_returned = User_Book.query.filter_by(User_id = id,Book_id = book_id,Status = "Returned").first()

   if user_book_returned:
      flash("You have already reviewed this book once", category = "error")
   else:
      user_book.feedback = feedback

   user_book.Status = "Returned"
   user_book.expiration_period = ""

   user = User.query.filter_by(id = id).first()
   user.count_access = user.count_access - 1
   db.session.commit()   
   flash(f'Book returned successfully. You can access {5-user.count_access} more books. Keep Browsing!!', category = "success")

   return redirect(f'/{id}/myBooks')

@views.route('/<int:id>/stats')
def stats(id):
   user = User.query.filter_by(id = id).first()

   user_books = User_Book.query.filter_by(User_id=id).filter(User_Book.Status.in_(["Issued", "Rejected", "Returned"])).all()

   if user_books:
      section_books_count = {}
      for user_book in user_books:
         book = Book.query.get(user_book.Book_id)
         section_name = book.section.Section_Title
         if section_name not in section_books_count:
            section_books_count[section_name] = {'Issued': 0, 'Rejected': 0}
         if user_book.Status == "Issued" or user_book.Status == "Returned":
            section_books_count[section_name]['Issued'] += 1
         elif user_book.Status == "Rejected":
            section_books_count[section_name]['Rejected'] += 1

      section_names = list(section_books_count.keys())
      issued_counts = [count['Issued'] for count in section_books_count.values()]
      rejected_counts = [count['Rejected'] for count in section_books_count.values()]

      plt.figure(figsize=(10, 6))
      bar_width = 0.35
      index = range(len(section_names))
      plt.bar(index, issued_counts, bar_width, label='Issued')
      plt.bar([i + bar_width for i in index], rejected_counts, bar_width, label='Rejected')
      plt.xlabel('Section')
      plt.ylabel('Number of Books')
      plt.title('Number of Issued and Rejected Books per Section')
      plt.xticks([i + bar_width / 2 for i in index], section_names, rotation=45, ha='right')
      plt.legend()

      plt.savefig(f'E:\e-books\IITM BSc in Data Science\Term 11\MAD-1 Project\MAD-1_Project_21f1004680\Website\static/bar_chart{id}.png')

   issued_books = User_Book.query.filter_by(User_id=id).filter(User_Book.Status.in_(["Issued", "Returned"])).all()

   if issued_books:
      section_books_count_pie = {}
      for user_book in issued_books:
         book = Book.query.get(user_book.Book_id)
         section_name = book.section.Section_Title
         section_books_count_pie[section_name] = section_books_count_pie.get(section_name, 0) + 1

      plt.figure(figsize=(10, 6))
      plt.pie(section_books_count_pie.values(), labels=section_books_count_pie.keys(), autopct='%1.1f%%', startangle=140)
      plt.title('Distribution of Sections for Completed Books')

      plt.savefig(f'E:\e-books\IITM BSc in Data Science\Term 11\MAD-1 Project\MAD-1_Project_21f1004680\Website\static/pie_chart{id}.png')


   return render_template('user_stats.html', user = user, user_books = user_books, issued_books = issued_books)

@views.route('/lib-stats')
def lib_stats():

   user_books = User_Book.query.filter_by(Status = "Issued").all()

   if user_books:
      section_books_count = {}
      for user_book in user_books:
         book = Book.query.get(user_book.Book_id)
         section_name = book.section.Section_Title
         if section_name not in section_books_count:
            section_books_count[section_name] = {'Issued': 0}
         if user_book.Status == "Issued" or user_book.Status == "Returned":
            section_books_count[section_name]['Issued'] += 1

      section_names = list(section_books_count.keys())
      issued_counts = [count['Issued'] for count in section_books_count.values()]

      plt.figure(figsize=(10, 6))
      bar_width = 0.35
      index = range(len(section_names))
      plt.bar(index, issued_counts, bar_width, label='Issued')
      plt.xlabel('Section')
      plt.ylabel('Number of Books')
      plt.title('Number of Issued Books per Section')
      plt.xticks([i + bar_width / 2 for i in index], section_names, rotation=45, ha='right')
      plt.legend()

      plt.savefig('E:\e-books\IITM BSc in Data Science\Term 11\MAD-1 Project\MAD-1_Project_21f1004680\Website\static/bar_chart.png')

   issued_books = User_Book.query.filter(User_Book.Status.in_(["Issued", "Returned"])).all()

   if issued_books:
      section_books_count_pie = {}
      for user_book in issued_books:
         book = Book.query.get(user_book.Book_id)
         section_name = book.section.Section_Title
         section_books_count_pie[section_name] = section_books_count_pie.get(section_name, 0) + 1

      plt.figure(figsize=(10, 6))
      plt.pie(section_books_count_pie.values(), labels=section_books_count_pie.keys(), autopct='%1.1f%%', startangle=140)
      plt.title('Distribution of Sections for Completed Books')

      plt.savefig('E:\e-books\IITM BSc in Data Science\Term 11\MAD-1 Project\MAD-1_Project_21f1004680\Website\static/pie_chart.png')

      return render_template('lib-stats.html', user_books = user_books, issued_books = issued_books)
