from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Que onda rey?</p>"

############CREACION DEL DB############
import mysql

mydb = mysql.connector.connect(
  host="127.0.0.1:5000",
  user="Franco",
  password="catalina"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE stock_DB")

