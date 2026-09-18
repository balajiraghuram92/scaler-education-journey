from fastapi import FastAPI
from routers import health, identity, agent_test

app = FastAPI()


app.include_router(health.router)
app.include_router(identity.router)
app.include_router(agent_test.router)