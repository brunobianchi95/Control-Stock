import jwt

jwt_key = "clavesecreta"
jwt_algorithm = "HS256"

base_url = "http://localhost:5000"


def encodeToken(id):
    return jwt.encode({"id": id}, jwt_key, algorithm=jwt_algorithm)


def decodeToken(token):
    try:
        tokenPayload = jwt.decode(token, jwt_key, algorithms=jwt_algorithm)
        return tokenPayload["id"]
    except:
        return None


def getAuthId(request):
    token = request.headers.get("authorization")
    if token == None:
        return None
    return decodeToken(token)


def formatUser(user):
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
    }