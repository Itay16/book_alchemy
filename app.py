import requests
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from data_models import Book, Author

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'

db = SQLAlchemy()
db.init_app(app)

@app.route('/', methods=['GET'])
def home():
  search_query = request.args.get('search')
  sort_by = request.args.get('sort')

  if search_query:
    books = Book.query.filter(Book.title.like(f"%{search_query}%")).all()
  else:
    books = Book.query.all()

  for book in books:
    author = Author.query.filter_by(id=book.author_id).first()
    if author:
      book.author = author.name
    else:
      book.author = "Unknown Author"

    # Fetch the cover image URL from the Open Library API
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{book.isbn}&jscmd=data&format=json"
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      book_info = data.get(f"ISBN:{book.isbn}", {})
      cover_info = book_info.get("cover", {})
      book.cover_image_url = cover_info.get("large", None)
    else:
      book.cover_image_url = None

  if sort_by == 'title':
    books.sort(key=lambda book: book.title)
  elif sort_by == 'author':
    books.sort(key=lambda book: book.author)

  deleted = request.args.get('deleted')
  return render_template('home.html', books=books, deleted=deleted)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
  if request.method == 'POST':
    title = request.form['title']
    publication_year = request.form['publication_year']
    author_id = request.form['author_id']

    # Search for the book using Open Library API
    url = f"https://openlibrary.org/search.json?q={title}&publish_year={publication_year}"
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      works = data.get('docs', [])
      if works:
        # Get the first matching work details
        work = works[0]
        isbn = work.get('isbn', [])[0] if 'isbn' in work else None
      else:
        isbn = None
    else:
      isbn = None

    # Create and add the book to the database
    new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
    db.session.add(new_book)
    db.session.commit()

    return f"{title} added successfully!"

  else:
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
  if request.method == "POST":
    name = request.form['name']
    birthdate = request.form['birthdate']
    date_of_death = request.form['date_of_death']

    new_author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death)
    db.session.add(new_author)
    db.session.commit()

    return f"{name} added successfully!"
  
  else:
    return render_template('add_author.html')


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
  book = Book.query.get_or_404(book_id)
  author_id = book.author_id

  # Perform the deletion after detaching
  db.session.delete(book)
  db.session.commit()

  # Check if the author has any other books
  author = Author.query.get(author_id)
  if not author.books:
    db.session.delete(author)
    db.session.commit()

  flash('The book has been deleted successfully.', 'success')
  return redirect(url_for('home', deleted=True))



if __name__ == '__main__':
  app.run(host="0.0.0.0", port=5002)