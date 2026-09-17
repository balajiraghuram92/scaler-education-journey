from fastapi import FastAPI
from routers import health, identity

app = FastAPI()


app.include_router(health.router)
app.include_router(identity.router)