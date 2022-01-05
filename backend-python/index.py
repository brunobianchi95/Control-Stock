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
    "CREATE TABLE `users` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `email` varchar(100) UNIQUE NOT NULL,"
    "  `password` TEXT NOT NULL,"
    "  `first_name` TEXT NOT NULL,"
    "  `last_name` TEXT NOT NULL,"
    "  `admin` BOOLEAN NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['stock'] = (
    "CREATE TABLE `stock` ("
    "  `cod` int(11) NOT NULL AUTO_INCREMENT,"
    "  `producto` TEXT NOT NULL,"
    "  `marca` TEXT NOT NULL,"
    "  `cantidad` INT NOT NULL,"
    "  `precio_c` INT NOT NULL,"
    "  `precio_v` INT NOT NULL,"
    "  PRIMARY KEY (`cod`)"
    ") ENGINE=InnoDB")

TABLES['compras'] = (
    "CREATE TABLE `compras` ("
    "  `no_c` int(11) NOT NULL AUTO_INCREMENT,"
    "  `user_id` int(11) NOT NULL,"
    "  `stock_cod` int(11) NOT NULL,"
    "  `producto` TEXT NOT NULL,"
    "  `marca` TEXT NOT NULL,"
    "  `proveedor` varchar(100) NOT NULL,"
    #"  `cuit` INT UNIQUE NOT NULL,"
    "  `cantidad` INT NOT NULL,"
    "  `precio_c` INT NOT NULL,"
    "  PRIMARY KEY (`no_c`), KEY `id` (`user_id`), KEY `cod` (`stock_cod`)"
    ") ENGINE=InnoDB")

TABLES['ventas'] = (
    "CREATE TABLE `ventas` ("
    "  `no_v` int(11) NOT NULL AUTO_INCREMENT,"
    "  `user_id` int(11) NOT NULL,"
    "  `stock_cod` int(11) NOT NULL,"
    "  `producto` TEXT NOT NULL,"
    "  `marca` TEXT NOT NULL,"
    "  `cuit_cliente` TEXT NOT NULL,"
    "  `cantidad` INT NOT NULL,"
    "  `precio_v` INT NOT NULL,"
    "  PRIMARY KEY (`no_v`), KEY `id` (`user_id`), KEY `cod` (`stock_cod`)"
    ") ENGINE=InnoDB")

TABLES['cliente'] = (
    "CREATE TABLE `cliente` ("
    "  `client_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `email` varchar(100) UNIQUE NOT NULL,"
    "  `first_name` TEXT NOT NULL,"
    "  `last_name` TEXT NOT NULL,"
    "  `cuit` TEXT NOT NULL,"
#    "  `compras` INT NOT NULL,"
#    "  `gasto` INT NOT NULL,"
    "  PRIMARY KEY (`client_id`)"
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