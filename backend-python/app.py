from flask import Flask, request
import index
import mysql.connector
from flask_login import LoginManager

app = Flask(__name__)

# Connect to the database
connection = mysql.connector.connect(
  database='stock_DB',
  host="Localhost",
  user="root",
  password="catalina"
)

@app.route("/api/signup", methods=["POST"])
def register():
    firstName = request.json["firstName"]
    lastName = request.json["lastName"]
    password = request.json["password"]
    email = request.json["email"]
    
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `users` (`email`, `password`, `first_name`, `last_name`, `admin`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (email, password, firstName, lastName, False))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    with connection.cursor() as cursor:
       # Read a single record
        sql = "SELECT `id`, `email` FROM `users` WHERE `email`=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        return {"id": result[0], "email": result[1]}


@app.route("/api/login", methods=["POST"])
def login():
