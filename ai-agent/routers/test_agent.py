from echo_agent import echo_agent
from fastapi import APIRouter

router = APIRouter()

@router.get("/echo")    
async def echo():
    result = await echo_agent.run("say hi")
    return result.output 