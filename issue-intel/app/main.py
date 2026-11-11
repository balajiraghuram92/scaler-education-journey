"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.approvals import router as approvals_router
from app.routers.fixes import router as fixes_router
from app.routers.health import router as health_router
from app.routers.metrics import router as metrics_router
from app.routers.reviews import router as reviews_router
from app.routers.runs import router as runs_router
from app.routers.tickets import router as tickets_router

app = FastAPI(title="issue-intel")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(tickets_router)
app.include_router(runs_router)
app.include_router(reviews_router)
app.include_router(fixes_router)
app.include_router(approvals_router)
