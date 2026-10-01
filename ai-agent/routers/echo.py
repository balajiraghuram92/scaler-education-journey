import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic_ai import Agent

from echo_agent import build_echo_agent
from rate_limit import rate_limited_user

logger = logging.getLogger(__name__)
router = APIRouter()


def get_echo_agent(request: Request) -> Agent:
    agent = getattr(request.app.state, "echo_agent", None)
    if agent is None:
        agent = build_echo_agent(request.app.state.settings)
        request.app.state.echo_agent = agent
    return agent


@router.get("/echo")
async def echo(
    _user: dict = Depends(rate_limited_user),
    agent: Agent = Depends(get_echo_agent),
):
    try:
        result = await agent.run("say hi")
    except Exception:
        logger.exception("echo: model call failed")
        raise HTTPException(status_code=502, detail="Upstream model call failed") from None
    return result.output
