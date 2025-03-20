import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# got this from the week 2 code
def DBconnection():
    try:
        con = mysql.connector.connect(
            host='cis2368db.cffyllx6uqih.us-east-1.rds.amazonaws.com',
            user='admin',
            password='MariyaTr4v1',
            database='cis2368db'
        )
        print('success')
        return con
        
    except Error as e:
        print('Database connection error:',e)
        return None
    

#get show books
@app.route('/show', methods =['GET'])
def show_book():

    con=DBconnection()
    if con is None:
        return jsonify({"error":"database error"})
    
    try:

        cursor=con.cursor(dictionary=True)
        cursor.execute('select * from books')
        book_data= cursor.fetchall()
        con.close()
        return jsonify(book_data)
    
    except Error as e:
        return jsonify({"error": "unable to show book"})
    
#Post add new book
@app.route('/add_book', methods=['POST'])
def add_book():
    con=DBconnection()
    if con is None:
        return jsonify({"error":"database connection error"})
    
    cursor =con.cursor()
    data=request.json

    needed_fields=['author', 'genre',  'status', 'title']
    for field in needed_fields:
        if field not in data:
            return jsonify({"error": f"missing {field}"})
    
    sql= 'insert into books(author, genre, status, title) values(%s,%s,%s,%s)'
    values=(data['author'], data['genre'], data['status'], data['title'])
    cursor.execute(sql,values)
    con.commit()
    con.close()
    return jsonify({'message':'book added'})

# Update 
@app.route('/update/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    con=DBconnection()
    if con is None:
        return jsonify({'error':"database connection failed"})
    
    cursor=con.cursor()
    data=request.json
    req_fields=['author', 'genre',  'status', 'title']

    for field in req_fields:
        if field not in data:
            return jsonify({'error':f'missing {field}'})
        
    sql= 'UPDATE books set  author=%s, genre=%s, status=%s, title=%s where id=%s'
    values= (data['author'], data['genre'], data['status'],data['title'],book_id)
    
    cursor.execute(sql,values)
    con.commit()
    con.close()

    return jsonify({'message':'book updated'})

#Delete 
@app.route('/delete/<int:book_id>', methods=['DELETE'])
def delete(book_id):
    con=DBconnection()
    if con is None:
        return jsonify({'error': "database connection failed"})
    
    try:

        cursor=con.cursor()
        sql= 'delete from books where id=%s' 
        values=(book_id,)
        cursor.execute(sql,values)
        con.commit()
        con.close()

        return jsonify({'message':'book deleted'})
    
    except:
        return jsonify({'error':'book not deleted'})


# GET all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT id, firstname, lastname, email FROM customers")
    customers = cursor.fetchall()
    con.close()
    return jsonify(customers), 200

# POST - Add a new customer (With Password Hashing)
@app.route('/customers', methods=['POST'])
def add_customer():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.json
    required_fields = ['firstname', 'lastname', 'email', 'password']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    hashed_password = generate_password_hash(data['password'])
    
    cursor = con.cursor()
    sql = "INSERT INTO customers (firstname, lastname, email, passwordhash) VALUES (%s, %s, %s, %s)"
    values = (data['firstname'], data['lastname'], data['email'], hashed_password)
    
    try:
        cursor.execute(sql, values)
        con.commit()
        return jsonify({"message": "Customer added"}), 201
    except Error as e:
        return jsonify({"error": f"Error adding customer: {str(e)}"}), 500
    finally:
        cursor.close()
        con.close()

# PUT - Update a customer
@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.json
    required_fields = ['firstname', 'lastname', 'email', 'password']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    hashed_password = generate_password_hash(data['password'])

    cursor = con.cursor()
    sql = "UPDATE customers SET firstname=%s, lastname=%s, email=%s, passwordhash=%s WHERE id=%s"
    values = (data['firstname'], data['lastname'], data['email'], hashed_password, customer_id)

    cursor.execute("SELECT * FROM customers WHERE id=%s", (customer_id,))
    if not cursor.fetchone():
        return jsonify({"error": "Customer not found"}), 404

    try:
        cursor.execute(sql, values)
        con.commit()
        return jsonify({"message": "Customer updated"}), 200
    except Error as e:
        return jsonify({"error": f"Error updating customer: {str(e)}"}), 500
    finally:
        cursor.close()
        con.close()

# DELETE - Remove a customer
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    cursor = con.cursor()
    cursor.execute("SELECT * FROM customers WHERE id=%s", (customer_id,))
    if not cursor.fetchone():
        return jsonify({"error": "Customer not found"}), 404

    sql = "DELETE FROM customers WHERE id=%s"
    
    try:
        cursor.execute(sql, (customer_id,))
        con.commit()
        return jsonify({"message": "Customer deleted"}), 200
    except Error as e:
        return jsonify({"error": f"Error deleting customer: {str(e)}"}), 500
    finally:
        cursor.close()
        con.close()

# GET all borrowing records
@app.route('/borrowings', methods=['GET'])
def get_borrowings():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM borrowingrecords")  # ✅ Correct table name
    borrowings = cursor.fetchall()
    con.close()
    return jsonify(borrowings), 200

# POST - Borrow a Book
@app.route('/borrow', methods=['POST'])
def borrow_book():
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.json
    required_fields = ['bookid', 'customerid', 'borrowdate']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400

    cursor = con.cursor()

    # Check if book is available
    cursor.execute("SELECT status FROM books WHERE id=%s", (data['bookid'],))
    book = cursor.fetchone()
    if not book or book[0] != 'available':
        return jsonify({"error": "Book is not available"}), 400

    # Check if customer already has a borrowed book
    cursor.execute("SELECT * FROM borrowingrecords WHERE customerid=%s AND returndate IS NULL", (data['customerid'],))
    if cursor.fetchone():
        return jsonify({"error": "Customer already has a borrowed book"}), 400

    # Insert borrowing record
    sql = "INSERT INTO borrowingrecords (bookid, customerid, borrowdate) VALUES (%s, %s, %s)"
    values = (data['bookid'], data['customerid'], data['borrowdate'])
    cursor.execute(sql, values)

    # Update book status to unavailable
    cursor.execute("UPDATE books SET status='unavailable' WHERE id=%s", (data['bookid'],))

    con.commit()
    con.close()

    return jsonify({'message': 'Book borrowed'}), 201

# PUT - Return a Book (Auto-Calculate Late Fee)
@app.route('/return/<int:borrow_id>', methods=['PUT'])
def return_book(borrow_id):
    con = DBconnection()
    if con is None:
        return jsonify({"error": "Database connection error"}), 500

    data = request.json
    if 'returndate' not in data:
        return jsonify({"error": "Missing returndate"}), 400

    cursor = con.cursor()

    # Fetch borrowing record
    cursor.execute("SELECT bookid, borrowdate FROM borrowingrecords WHERE id=%s AND returndate IS NULL", (borrow_id,))
    record = cursor.fetchone()

    if not record:
        return jsonify({"error": "Borrowing record not found"}), 404

    bookid, borrowdate = record
    borrowdate = datetime.strptime(str(borrowdate), '%Y-%m-%d')
    returndate = datetime.strptime(data['returndate'], '%Y-%m-%d')

    # Calculate late fee ($1 per day after 10 days)
    days_borrowed = (returndate - borrowdate).days
    late_fee = max(0, days_borrowed - 10)

    # Update borrowing record with return date and late fee
    sql = "UPDATE borrowingrecords SET returndate=%s, late_fee=%s WHERE id=%s"
    values = (data['returndate'], late_fee, borrow_id)
    cursor.execute(sql, values)

    # Mark book as available
    cursor.execute("UPDATE books SET status='available' WHERE id=%s", (bookid,))

    con.commit()
    con.close()

    return jsonify({'message': 'Book returned', 'late_fee': late_fee}), 200

# DELETE - Remove a borrowing record
@app.route('/delete_borrowing/<int:borrow_id>', methods=['DELETE'])
def delete_borrowing(borrow_id):
    con = DBconnection()
    if con is None:
        return jsonify({'error': "Database connection failed"}), 500

    cursor = con.cursor()

    # Check if borrowing record exists
    cursor.execute("SELECT * FROM borrowingrecords WHERE id=%s", (borrow_id,))
    if not cursor.fetchone():
        return jsonify({"error": "Borrowing record not found"}), 404

    # Delete the borrowing record
    sql = "DELETE FROM borrowingrecords WHERE id=%s"
    cursor.execute(sql, (borrow_id,))
    con.commit()
    con.close()

    return jsonify({'message': 'Borrowing record deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
