import os

JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY")
if not JWT_SIGNING_KEY:
    raise RuntimeError("JWT_SIGNING_KEY environment variable is unset")


MUSE_AI_API_KEY = os.environ.get("MUSE_AI_API_KEY")
if not MUSE_AI_API_KEY:
    raise RuntimeError("MUSE_AI_API_KEY environment variable is unset")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is unset")

JWT_ISSUER = os.environ.get("JWT_ISSUER", "neuralascent")
JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE", "neuralascent-app")
JWT_COOKIE_NAME = os.environ.get("JWT_COOKIE_NAME", "na_auth")



