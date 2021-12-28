from flask import Flask

index = Flask(__name__)

############CREACION DEL DB############
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
    "CREATE TABLE `users` ("
    "  `ID` int(11) NOT NULL AUTO_INCREMENT,"
    "  `email` varchar(100) UNIQUE NOT NULL,"
    "  `password` TEXT NOT NULL,"
    "  `first_name` TEXT NOT NULL,"
    "  `last_name` TEXT NOT NULL,"
    "  `admin` BOOLEAN NOT NULL,"
    "  PRIMARY KEY (`ID`)"
    ") ENGINE=InnoDB")

TABLES['stock'] = (
    "CREATE TABLE `stock` ("
    "  `COD` int(11) NOT NULL AUTO_INCREMENT,"
    "  `Bebida` varchar(14) NOT NULL,"
    "  `Brand` varchar(16) NOT NULL,"
    "  `Cant` INT NOT NULL,"
    "  PRIMARY KEY (`COD`)"
    ") ENGINE=InnoDB")

TABLES['ventas'] = (
    "CREATE TABLE `ventas` ("
    "  `NO_V` int(11) NOT NULL AUTO_INCREMENT,"
    "  `ID` int(11) NOT NULL,"
    "  `COD` int(11) NOT NULL,"
    "  `Cant` INT NOT NULL,"
    "  PRIMARY KEY (`NO_V`), KEY `ID` (`ID`), KEY `COD` (`COD`)"
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