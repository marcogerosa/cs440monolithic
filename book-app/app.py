from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

def init_db():
    connection = get_db_connection()
    with open('schema.sql', 'r') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    connection = get_db_connection()
    books = connection.execute('SELECT * FROM books').fetchall()
    connection.close()
    return render_template('books.html', books=books)

@app.route('/books/<int:book_id>')
def book_details(book_id):
    connection = get_db_connection()
    book = connection.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    reviews = connection.execute('SELECT * FROM reviews WHERE book_id = ?', (book_id,)).fetchall()
    connection.close()
    return render_template('reviews.html', book=book, reviews=reviews)

@app.route('/books/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    year = request.form['year']
    
    connection = get_db_connection()
    connection.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
                (title, author, year))
    connection.commit()
    connection.close()
    flash('Book added successfully!')
    return redirect(url_for('books'))

@app.route('/reviews/add', methods=['POST'])
def add_review():
    book_id = request.form['book_id']
    rating = request.form['rating']
    comment = request.form['comment']
    reviewer = request.form['reviewer']
    date = datetime.now().strftime("%Y-%m-%d")
    
    connection = get_db_connection()
    connection.execute('INSERT INTO reviews (book_id, rating, comment, reviewer, date) VALUES (?, ?, ?, ?, ?)',
                (book_id, rating, comment, reviewer, date))
    connection.commit()
    connection.close()
    flash('Review added successfully!')
    return redirect(url_for('book_details', book_id=book_id))

@app.route('/api/books')
def api_books():
    connection = get_db_connection()
    books = connection.execute('SELECT * FROM books').fetchall()
    connection.close()
    return jsonify([dict(book) for book in books])

@app.route('/api/reviews/<int:book_id>')
def api_reviews(book_id):
    connection = get_db_connection()
    reviews = connection.execute('SELECT * FROM reviews WHERE book_id = ?', (book_id,)).fetchall()
    connection.close()
    return jsonify([dict(review) for review in reviews])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
