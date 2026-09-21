
import observability
from fastapi import FastAPI
from routers import health, identity, test_agent, test_graph
from contextlib import asynccontextmanager 
from db import pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool.open()
    yield
    await pool.close()


app = FastAPI(lifespan = lifespan)


app.include_router(health.router)
app.include_router(identity.router)
app.include_router(test_agent.router)
app.include_router(test_graph.router)
