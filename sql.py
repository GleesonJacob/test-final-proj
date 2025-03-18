import mysql.connector
from mysql.connector import Error


# Function to establish database connection from Week 1.
def DBconnection():
    try:
        con = mysql.connector.connect(
            host='cis2368db.cffyllx6uqih.us-east-1.rds.amazonaws.com',
            user='admin',
            password='MariyaTr4v1',
            database='cis2368db'
        )
        if con.is_connected():
            print("Connected to MySQL database successfully.")
        return con
    except Error as e:
        print("Connection error:", e)
        return None

# Establish database connection
mycon = DBconnection()

if mycon:
    mycursor = mycon.cursor(dictionary=True)


