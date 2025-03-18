import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify

app = Flask(__name__)

# got this from the week 2 code
def DBconnection():
    try:
        con = mysql.connector.connect(
            host="cis2368db.ci5imtpzea1r.us-east-1.rds.amazonaws.com",
            user="admin",
            password="HoustonTexas",
            database="cis2368DB"
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





if __name__ == '__main__':
    app.run(debug=True)

