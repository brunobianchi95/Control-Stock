import jwt
import time
import hashlib

jwt_key = "clavesecreta"
jwt_algorithm = "HS256"

base_url = "http://localhost:5000"


def encodeToken(id: str) -> str:
    current_time = int(time.time())
    return jwt.encode({"id": id, "iat": current_time}, jwt_key, algorithm=jwt_algorithm)


# decodeToken: str -> (str, int)
def decodeToken(token):
    tokenPayload = jwt.decode(token, jwt_key, algorithms=jwt_algorithm)
    return (tokenPayload["id"], tokenPayload["iat"])


def hashPassword(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def getAuthId(request):
    token = request.headers.get("authorization")
    if token == None:
        return None
    try:
        (id, _) = decodeToken(token)
        return id
    except:
        return None


def formatUser(user):
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
    }