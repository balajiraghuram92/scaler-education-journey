import os
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request

JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY")
if not JWT_SIGNING_KEY:
    raise RuntimeError("JWT_SIGNING_KEY environment variable is unset")

JWT_ISSUER = os.environ.get("JWT_ISSUER", "neuralascent")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "neuralascent-app")
JWT_COOKIE_NAME = os.environ.get("JWT_COOKIE_NAME", "na_auth")

app = FastAPI()


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
