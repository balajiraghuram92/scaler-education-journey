from fastapi import FastAPI
from routers import health, identity, test_agent, test_graph

app = FastAPI()


app.include_router(health.router)
app.include_router(identity.router)
app.include_router(test_agent.router)
app.include_router(test_graph.router)
