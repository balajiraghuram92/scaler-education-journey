from fastapi import APIRouter
from echo_graph import agent_graph

router = APIRouter()
@router.get("/agent_test")
def test_agentGraph():
    result = agent_graph.invoke({"input_txt": "Hello"})
    return result
