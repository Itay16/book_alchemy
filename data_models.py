from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()

# Create a database connection
engine = create_engine('sqlite:///data/library.sqlite')

# Create a session
Session = sessionmaker(bind=engine)
session = Session()
db = SQLAlchemy()

class Author(db.Model):
  __tablename__ = 'authors'

  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String)
  birth_date = Column(String)
  date_of_death = Column(String)

  def __repr__(self):
    return f'Author(author_id={self.id}, author_name={self.name}, author_birth_date={self.birth_date}, author_date_of_death={self.date_of_death})'


class Book(db.Model):
  __tablename__ = 'books'

  id = Column(Integer, primary_key=True, autoincrement=True)
  isbn = Column(Integer)
  title = Column(String)
  publication_year = Column(String)
  author_id = Column(Integer, ForeignKey('authors.id'))

  def __repr__(self):
    return f'Book(id={self.id}, isbn={self.isbn}, title={self.title}, publication_year={self.publication_year}, author_id={self.author_id})'
