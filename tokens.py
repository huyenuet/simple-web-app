import jwt
from datetime import datetime, timedelta
import schemas

# Secret key used to sign and verify JWTs
SECRET_KEY = "mysecretkey"

def generate_token(user: schemas.User):
    # Generate a JWT containing the user ID and an expiration time
    token = jwt.encode({
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")
    return token

def  decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload
