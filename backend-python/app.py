from flask import Flask, request, jsonify
import index
import utils
import mysql.connector

app = Flask(__name__)

# Connect to the database #
connection = mysql.connector.connect(
  database='stock_DB',
  host="Localhost",
  user="root",
  password="catalina"
)
 

# (connection, request) -> (ID, Bool, Error)
def isAdmin(connection, req):
  with connection.cursor() as cursor:
    adminId = utils.getAuthId(req)
    if adminId == None:
      cursor.close()
      return None, False, ({"error": "no estas logueado"}, 400)
    cursor.execute("SELECT admin FROM users WHERE (user_id = %s)", (int(adminId),))
    result = cursor.fetchone()
    isAdmin = result[0] == True

    if isAdmin:
      return int(adminId), True, None

    return int(adminId), False, ({"error": "no sos admin"}, 403)


# SIGNUP #
@app.route("/api/signup", methods=["POST"])
def register():
  firstName = request.json["firstName"]
  lastName = request.json["lastName"]
  password = request.json["password"]
  email = request.json["email"]
    
  with connection.cursor() as cursor:
    query = "INSERT INTO users (email, password, first_name, last_name, admin) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (email, password, firstName, lastName, False))
    connection.commit()

  with connection.cursor() as cursor:
    query = "SELECT user_id, email FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    return {"id": result[0], "email": result[1]}

# LOGIN #
@app.route("/api/login", methods=["POST"])
def login():
  email = request.json["email"]
  password = request.json["password"]

  with connection.cursor() as cursor:
    query = "SELECT user_id, email, password FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    if result[1] == email and result[2] == password:
      token = utils.encodeToken(result[0])
      return {"token":token}
    return {"mensaje":"Usuario o contraseña incorrecto"}, 400


# DELETE USER SIENDO ADMIN #
@app.route("/api/admin/deleteUser/<id>", methods=["DELETE"])
def deleteUser(id):
  _, admin, err = isAdmin(connection, request) 
  if admin == False:
    return err

  with connection.cursor() as cursor:
    cursor.execute("DELETE FROM users WHERE (user_id = %s)", (id,))
    connection.commit()
    return {"message": "usuario eliminado"}

# COMPRAR Y REGISTRAR PRODUCTO #
@app.route("/api/buy", methods=["POST"])
def regProduct():
  producto = request.json["producto"]
  marca = request.json["marca"]
  cantidad = request.json["cantidad"]
  proveedor = request.json["proveedor"]
  precio_c = int(request.json["precio_c"])   
  
  adminId, admin, err = isAdmin(connection, request) 
  if admin == False:
    return err

  with connection.cursor() as cursor:
    query = "SELECT producto_id FROM productos WHERE (producto=%s AND marca=%s)"
    cursor.execute(query, (producto, marca))
    result = cursor.fetchone()
              
    if result != None:
      producto_id = result[0]
      with connection.cursor() as cursor:
        try:
          queryI = "INSERT INTO compras (user_id, producto_id, proveedor, cantidad, precio_c) VALUES (%s, %s, %s, %s, %s)"
          cursor.execute(queryI, (adminId, producto_id, proveedor, cantidad, precio_c))
          compra_id = cursor.lastrowid

          queryS = "SELECT stock FROM productos WHERE producto_id = %s"
          cursor.execute(queryS, (producto_id,))
          prodSeleccionado = cursor.fetchone()

          existencia = int(prodSeleccionado[0])
          suma = existencia + int(cantidad)
          queryU = "UPDATE productos SET stock= %s, compra_id= %s WHERE producto_id= %s"
          cursor.execute(queryU, (suma, compra_id, producto_id))

          connection.commit()
          return {"mensaje": "registro ok", "compra_id": compra_id}
        except:
          connection.rollback()
          return {"mensaje": "Falla del servidor" }, 500
    
    queryI = "INSERT INTO productos (producto, marca, stock) VALUES (%s, %s, %s)"
    cursor.execute(queryI, (producto, marca, cantidad))
    producto_id = cursor.lastrowid

    queryI = "INSERT INTO compras (user_id, producto_id, proveedor, cantidad, precio_c) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(queryI, (adminId, producto_id, proveedor, cantidad, precio_c))
    compra_id = cursor.lastrowid

    queryU = "UPDATE productos SET compra_id= %s WHERE producto_id= %s"
    cursor.execute(queryU, (compra_id, producto_id))

    connection.commit()
    return {"mensaje": "registro ok", "compraId": compra_id}
  

# ANULAR COMPRA #
@app.route("/api/buy/cancel/<n>", methods=["DELETE"])
def buyCancel(n):

 _, admin, err = isAdmin(connection, request) 
 if admin == False:
    return err

 with connection.cursor() as cursor:
  selectCompra = "SELECT stock_cod, cantidad FROM compras WHERE no_c=%s"
  cursor.execute(selectCompra, (n,))
  compra = cursor.fetchone()
  stock_cod = compra[0]
  cantidad = compra[1]

  selectProd = "SELECT cantidad FROM stock WHERE cod = %s"
  cursor.execute(selectProd, (stock_cod, ))
  prod = cursor.fetchone()
  cantidadStock = int(prod[0])
  connection.commit()

  with connection.cursor() as cursor:
    updateStock = "UPDATE stock SET cantidad=%s WHERE cod=%s"
    refund = cantidadStock - cantidad
    cursor.execute(updateStock, (refund, stock_cod))
    deleteCompra = "DELETE FROM compras WHERE no_c = %s"
    cursor.execute(deleteCompra, (n,))
    connection.commit()
    return {"message": "compra eliminada"}
 
 

# VENDER PRODUCTO #
@app.route("/api/sell", methods=["POST"])
def sellProduct():
  
  producto_id = request.json["product_id"]
  cantidad = int(request.json["cantidad"])
  
  # cliente
  email = request.json["email"]


 # Se fija si existe el cliente y si no existe lo crea
  client_id = None

  with connection.cursor() as cursor:
    query = "SELECT client_id FROM clientes WHERE email = %s" 
    cursor.execute(query, (email,))
    cliente = cursor.fetchone()

    if cliente == None:
      first_name = request.json["first_name"]
      last_name = request.json["last_name"]
      cuit = int(request.json["cuit"])

      register = "INSERT INTO clientes (email, first_name, last_name, cuit) VALUES (%s, %s, %s, %s)"
      cursor.execute(register, (email, first_name, last_name, cuit))    
      client_id = cursor.lastrowid
    else:
      client_id = cliente[0]

      
  userId = utils.getAuthId(request)
  if userId == None:
    return {"error": "no estas logueado"}, 400

  with connection.cursor() as cursor:
    query = "SELECT productos.producto_id, stock, precio_c FROM productos INNER JOIN compras ON productos.compra_id = compras.compra_id WHERE producto_id= %s" 
    cursor.execute(query, (producto_id, ))
    result = cursor.fetchone()

    if result == None:
      return {"mensaje":"producto no encontrado"}

    producto_id = result[0]
    existencia = int(result[1])
    precio_v = int(result[2]) * 1.25

    if existencia < cantidad:
      cursor.close()
      return {"error": "no hay stock"}, 403

    query = "INSERT INTO ventas (user_id, producto_id, client_id, cantidad, precio_v) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (userId, producto_id, client_id, cantidad, precio_v))    
    venta = existencia - cantidad
    update = "UPDATE productos SET stock=%s WHERE producto_id=%s"
    cursor.execute(update, (venta, producto_id))
    connection.commit()
    return {"mensaje": "venta ok"}



# ANULAR VENTA #
@app.route("/api/sell/cancel", methods=["DELETE"])
def sellCancel():
  user_id = request.json["user_id"]
  stock_cod = request.json["stock_cod"]
  producto = request.json["producto"]
  marca = request.json["marca"]
  cuit_cliente = request.json["cuit_cliente"]
  cantidad_vendida = int(request.json["cantidad"])  
  precio_v = request.json["precio_v"]

  with connection.cursor() as cursor:
    adminId = utils.getAuthId(request)
    adminId = int(adminId)
    if adminId == None:
      cursor.close()
      return {"error": "no estas logueado"}, 400
    cursor.execute("SELECT id, admin FROM users WHERE id = %s", (adminId,))
    result = cursor.fetchone()
    if result[1] == True:
      selectVenta = "SELECT no_v, cantidad FROM ventas WHERE user_id = %s AND stock_cod = %s producto = %s AND marca = %s AND cuit_cliente=%s AND cantidad = %s AND precio_v=%s"
      cursor.execute(selectVenta, (user_id, stock_cod,producto, marca, cuit_cliente, cantidad_vendida, precio_v))
      venta = cursor.fetchone()
      NO_V = venta[0]
      cantidad = venta[1]
      selectProd = "SELECT cantidad FROM stock WHERE cod = %s"
      cursor.execute(selectProd, (stock_cod, ))
      prod = cursor.fetchone()
      cantidadStock = int(prod[0])
      connection.commit()

      with connection.cursor() as cursor:
        if cantidad_vendida == cantidad: 
          updateStock = "UPDATE stock SET cantidad=%s WHERE cod=%s"
          refund = cantidadStock + cantidad_vendida
          cursor.execute(updateStock, (refund, stock_cod))
          deleteVenta = "DELETE FROM ventas WHERE no_v = %s"
          cursor.execute(deleteVenta, (NO_V,))
          connection.commit()
          return {"message": "venta eliminada"}
        return {"error":"no coinciden las cantidades"}

    cursor.close()
    return {"error": "no sos admin"}, 403


# OBTENER LISTA PRODUCTOS #
@app.route("/api/products", methods=["GET"])
def getProduct():
     
  with connection.cursor() as cursor:  
    query = "SELECT productos.producto_id, producto, marca, stock, precio_c FROM productos INNER JOIN compras ON productos.compra_id = compras.compra_id" 
    cursor.execute(query, )
    result = cursor.fetchall()

    productos = []
    for row in result:
      product = {
        "producto_id": row[0],
        "producto": row[1],
        "marca": row[2],
        "stock": row[3],
        "precio_v": row[4] * 1.25
      }
      productos.append(product)

    return jsonify(productos)