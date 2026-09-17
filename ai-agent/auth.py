
import jwt
from fastapi import HTTPException, Request
from config import JWT_COOKIE_NAME,JWT_SIGNING_KEY,JWT_ISSUER,JWT_AUDIENCE

def get_current_user(request: Request) -> dict:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, param = auth_header.partition(" ")
        if scheme.lower() == "bearer" and param:
            token = param.strip()

    if not token:
        token = request.cookies.get(JWT_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        claims = jwt.decode(
            token,
            JWT_SIGNING_KEY,
            algorithms=["HS256"],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
        return claims
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
