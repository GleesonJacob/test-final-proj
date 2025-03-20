import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Database Connection
def DBconnection():
    try:
        connection = mysql.connector.connect(
            host='cis2368db.cffyllx6uqih.us-east-1.rds.amazonaws.com',
            user='admin',
            password='MariyaTr4v1',
            database='cis2368db'
        )
        if connection.is_connected():
            print("Connected to MySQL database successfully.")
        return connection
    except mysql.connector.Error as e:
        print("Connection error:", e)
        return None

# GET all books
@app.route('/books', methods=['GET'])
def get_books():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    con.close()
    return jsonify(books), 200

# POST - Add new book
@app.route('/books', methods=['POST'])
def add_book():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    data = request.json
    if not all(key in data for key in ['author', 'genre', 'status', 'title']):
        return jsonify({"error": "Missing fields"}), 400

    cursor = con.cursor()
    sql = "INSERT INTO books (author, genre, status, title) VALUES (%s, %s, %s, %s)"
    values = (data['author'], data['genre'], data['status'], data['title'])
    cursor.execute(sql, values)
    con.commit()
    con.close()

    return jsonify({'message': 'Book added'}), 201

# PUT - Update a book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    con = DBconnection()
    if con is None:
        return jsonify({'error': "database connection failed"}), 500

    data = request.json
    cursor = con.cursor()
    sql = "UPDATE books SET author=%s, genre=%s, status=%s, title=%s WHERE id=%s"
    values = (data['author'], data['genre'], data['status'], data['title'], book_id)
    cursor.execute(sql, values)
    con.commit()
    con.close()

    return jsonify({'message': 'Book updated'}), 200

# DELETE - Remove a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    con = DBconnection()
    if con is None:
        return jsonify({'error': "database connection failed"}), 500

    cursor = con.cursor()
    sql = "DELETE FROM books WHERE id=%s"
    cursor.execute(sql, (book_id,))
    con.commit()
    con.close()

    return jsonify({'message': 'Book deleted'}), 200

# GET all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    con.close()
    return jsonify(customers), 200

# POST - Add new customer (Password Hashing)
@app.route('/customers', methods=['POST'])
def add_customer():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    data = request.json
    if not all(key in data for key in ['firstname', 'lastname', 'email', 'password']):
        return jsonify({"error": "Missing fields"}), 400

    hashed_password = generate_password_hash(data['password'])
    cursor = con.cursor()
    sql = "INSERT INTO customers (firstname, lastname, email, passwordhash) VALUES (%s, %s, %s, %s)"
    values = (data['firstname'], data['lastname'], data['email'], hashed_password)
    cursor.execute(sql, values)
    con.commit()
    con.close()

    return jsonify({'message': 'Customer added'}), 201

# POST - Borrow a book
@app.route('/borrow', methods=['POST'])
def borrow_book():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    data = request.json
    if not all(key in data for key in ['bookid', 'customerid', 'borrowdate']):
        return jsonify({"error": "Missing fields"}), 400

    cursor = con.cursor()

    # Check book availability
    cursor.execute("SELECT status FROM books WHERE id=%s", (data['bookid'],))
    book = cursor.fetchone()
    if not book or book[0] != 'available':
        return jsonify({"error": "Book is not available"}), 400

    # Check if customer already has a borrowed book
    cursor.execute("SELECT * FROM borrowingrecords WHERE customerid=%s AND returndate IS NULL", (data['customerid'],))
    if cursor.fetchone():
        return jsonify({"error": "Customer already has a borrowed book"}), 400

    sql = "INSERT INTO borrowingrecords (bookid, customerid, borrowdate) VALUES (%s, %s, %s)"
    values = (data['bookid'], data['customerid'], data['borrowdate'])
    cursor.execute(sql, values)

    cursor.execute("UPDATE books SET status='unavailable' WHERE id=%s", (data['bookid'],))
    con.commit()
    con.close()

    return jsonify({'message': 'Book borrowed'}), 201

# PUT - Return a book (Calculate Late Fee)
@app.route('/return/<int:borrow_id>', methods=['PUT'])
def return_book(borrow_id):
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    data = request.json
    if 'returndate' not in data:
        return jsonify({"error": "Missing returndate"}), 400

    cursor = con.cursor()
    cursor.execute("SELECT bookid, borrowdate FROM borrowingrecords WHERE id=%s AND returndate IS NULL", (borrow_id,))
    record = cursor.fetchone()

    if not record:
        return jsonify({"error": "Borrowing record not found"}), 404

    bookid, borrowdate = record
    borrowdate = datetime.strptime(str(borrowdate), '%Y-%m-%d')
    returndate = datetime.strptime(data['returndate'], '%Y-%m-%d')

    late_fee = max(0, (returndate - borrowdate).days - 10)

    sql = "UPDATE borrowingrecords SET returndate=%s, late_fee=%s WHERE id=%s"
    values = (data['returndate'], late_fee, borrow_id)
    cursor.execute(sql, values)

    cursor.execute("UPDATE books SET status='available' WHERE id=%s", (bookid,))
    con.commit()
    con.close()

    return jsonify({'message': 'Book returned', 'late_fee': late_fee}), 200

# GET - View all active borrowings
@app.route('/borrowings', methods=['GET'])
def get_borrowings():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "database connection error"}), 500

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM borrowingrecords WHERE returndate IS NULL")
    borrowings = cursor.fetchall()
    con.close()
    return jsonify(borrowings), 200

if __name__ == '__main__':
    app.run(debug=True)
