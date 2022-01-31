from flask import Flask

index = Flask(__name__)

## CREACION DE DB ##
import mysql.connector
from mysql.connector import errorcode

cnx = mysql.connector.connect(
  host="Localhost",
  user="root",
  password="catalina"
)
cursor = cnx.cursor()

#creacion tablas#
DB_NAME = 'stock_DB'

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

TABLES = {}
TABLES['users'] = (
    "CREATE TABLE users ("
    "  user_id int(11) NOT NULL AUTO_INCREMENT,"
    "  email varchar(100) UNIQUE NOT NULL,"
    "  password TEXT NOT NULL,"
    "  first_name TEXT NOT NULL,"
    "  last_name TEXT NOT NULL,"
    "  admin BOOLEAN NOT NULL,"
    "  verified_email BOOLEAN NOT NULL,"
    "  PRIMARY KEY (user_id)"
    ") ENGINE=InnoDB")

TABLES['productos'] = (
    "CREATE TABLE productos ("
    "  producto_id int(11) NOT NULL AUTO_INCREMENT,"
    "  compra_id INT REFERENCES compras(compra_id) ON DELETE SET NULL,"
    "  producto TEXT NOT NULL,"
    "  marca TEXT NOT NULL,"
    "  stock INT NOT NULL,"
    "  PRIMARY KEY (producto_id)"
    ") ENGINE=InnoDB")

TABLES['compras'] = (
    "CREATE TABLE compras ("
    "  compra_id int(11) NOT NULL AUTO_INCREMENT,"
    "  user_id INT REFERENCES users(user_id) ON DELETE SET NULL,"
    "  producto_id INT REFERENCES productos(producto_id) ON DELETE SET NULL,"
    "  proveedor varchar(100) NOT NULL,"
    "  cantidad INT NOT NULL," 
    "  precio_c INT NOT NULL,"
    "  tiempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (compra_id) "
    ") ENGINE=InnoDB")

TABLES['ventas'] = (
    "CREATE TABLE ventas ("
    "  venta_id int(11) NOT NULL AUTO_INCREMENT,"
    "  user_id INT REFERENCES users(user_id) ON DELETE SET NULL,"
    "  client_id INT REFERENCES users(client_) ON DELETE SET NULL,"
    "  tiempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (venta_id) "
    ") ENGINE=InnoDB")

TABLES['detalle_ventas'] = (
    "CREATE TABLE detalle_ventas ("
    "  numero_id int(11) NOT NULL AUTO_INCREMENT,"
    "  venta_id INT REFERENCES ventas(venta_id) ON DELETE SET NULL,"
    "  producto_id INT REFERENCES productos(producto_id) ON DELETE SET NULL,"
    "  cantidad INT NOT NULL," 
    "  precio_v INT NOT NULL,"
    "  PRIMARY KEY (numero_id) "
    ") ENGINE=InnoDB")

TABLES['clientes'] = (
    "CREATE TABLE clientes ("
    "  client_id int(11) NOT NULL AUTO_INCREMENT,"
    "  email varchar(100) UNIQUE NOT NULL,"
    "  first_name TEXT NOT NULL,"
    "  last_name TEXT NOT NULL,"
    "  cuit TEXT NOT NULL,"
    "  PRIMARY KEY (client_id)"
    ") ENGINE=InnoDB")


TABLES['messages'] = (
    "CREATE TABLE messages ("
    "  message_id int(11) NOT NULL AUTO_INCREMENT,"
    "  sender_id int REFERENCES users(user_id) ON DELETE SET NULL,"
    "  receiver_id int REFERENCES users(user_id) ON DELETE SET NULL,"
    "  message TEXT NOT NULL,"
    "  is_read BOOLEAN NOT NULL,"
    "  PRIMARY KEY (message_id)"
    ") ENGINE=InnoDB")


try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()