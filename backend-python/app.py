from flask import Flask, request
import index
import utils
import mysql.connector

app = Flask(__name__)

# Connect to the database
connection = mysql.connector.connect(
  database='stock_DB',
  host="Localhost",
  user="root",
  password="catalina"
)

#SIGNUP#
@app.route("/api/signup", methods=["POST"])
def register():
    firstName = request.json["firstName"]
    lastName = request.json["lastName"]
    password = request.json["password"]
    email = request.json["email"]
    
    with connection.cursor() as cursor:
        # Create a new record
        query = "INSERT INTO `users` (`email`, `password`, `first_name`, `last_name`, `admin`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (email, password, firstName, lastName, False))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

    with connection.cursor() as cursor:
       # Read a single record
        query = "SELECT `id`, `email` FROM `users` WHERE `email`=%s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return {"id": result[0], "email": result[1]}

#LOGIN#
@app.route("/api/login", methods=["POST"])
def login():
  email = request.json["email"]
  password = request.json["password"]
  with connection.cursor() as cursor:
    query = "SELECT `id`, `email`, `password` FROM `users` WHERE `email`=%s AND `password`=%s"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    if result[1] == email and result[2] == password:
      token = utils.encodeToken(result[0])
      return {"token":token}
    return {"mensaje":"Usuario o contraseña incorrecto"}, 400


#DELETE USER SIENDO ADMIN#
@app.route("/api/admin/deleteUser/<id>", methods=["DELETE"])
def deleteUser(id):
  with connection.cursor() as cursor:
    adminId = utils.getAuthId(request)
    adminId = int(adminId)
    if adminId == None:
        cursor.close()
        return {"error": "no estas logueado"}, 400
    cursor.execute("SELECT `id`, `admin` FROM `users` WHERE (`ID` = %s)", (adminId,))
    result = cursor.fetchone()
    if result[1] == True:
        cursor.execute("DELETE FROM `users` WHERE (`ID` = %s)", (id,))
        connection.commit()
        return {"message": "usuario eliminado"}
    cursor.close()
    return {"error": "no sos admin"}, 403

#CREAR PRODUCTO#
@app.route("/api/regProduct", methods=["POST"])
def regProduct():
    producto = request.json["producto"]
    marca = request.json["marca"]
    cantidad = request.json["cantidad"]
    
    with connection.cursor() as cursor:
      adminId = utils.getAuthId(request)
      adminId = int(adminId)
      
      if adminId == None:
        cursor.close()
        return {"error": "no estas logueado"}, 400
      cursor.execute("SELECT `id`, `admin` FROM `users` WHERE (`ID` = %s)", (adminId,))
      result = cursor.fetchone()
      if result[1] == True:
        query = "INSERT INTO `stock` (`producto`, `marca`, `cantidad`) VALUES (%s, %s, %s)"
        cursor.execute(query, (producto, marca, cantidad))
        connection.commit()

        with connection.cursor() as cursor:
          query = "SELECT `COD`, `producto`, `marca` FROM `stock` WHERE `producto`=%s AND `marca`=%s"
          cursor.execute(query, (producto, marca))
          result = cursor.fetchone()
          return {"COD": result[0], "producto": result[1], "marca": result[2]}

      cursor.close()
      return {"error": "no sos admin"}, 403

#COMPRAR PRODUCTO#
@app.route("/api/add/<COD>", methods=["POST"])
def addProduct(COD):
    proveedor = request.json["proveedor"]
    cantidad = request.json["cantidad"]
    precioC = request.json["precioC"]
    stock_COD = COD
    
    with connection.cursor() as cursor:
      adminId = utils.getAuthId(request)
      adminId = int(adminId)
      
      if adminId == None:
        cursor.close()
        return {"error": "no estas logueado"}, 400
      cursor.execute("SELECT `id`, `admin` FROM `users` WHERE (`ID` = %s)", (adminId,))
      result = cursor.fetchone()
      if result[1] == True:
        query = "INSERT INTO `compras` (`user_ID`, `stock_COD`, `proveedor`, `cantidad`, `precioC`) VALUES (%s, %s, %s,  %s, %s)"
        cursor.execute(query, (adminId, stock_COD, proveedor, cantidad, precioC))
        with connection.cursor() as cursor:
          query = "SELECT `cantidad` FROM `stock` WHERE `COD` = %s" 
          cursor.execute(query, (COD,))
          existencia = cursor.fetchone()
          suma = int(existencia[0]) + int(cantidad)
          query = "UPDATE `stock` SET `cantidad`=%s WHERE `COD`=%s"
          cursor.execute(query, (suma, COD))
          result = cursor.fetchone()
          connection.commit()
          return {"mensaje": "compra ok"}

      cursor.close()
      return {"error": "no sos admin"}, 403
