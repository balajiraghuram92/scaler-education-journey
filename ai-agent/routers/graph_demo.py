from fastapi import APIRouter, Depends

import observability
from auth import get_current_user
from echo_graph import agent_graph

router = APIRouter()


@router.get("/agent_test")
def agent_graph_demo(_user: dict = Depends(get_current_user)):
    return agent_graph.invoke(
        {"input_txt": "Hello"},
        config={"callbacks": observability.langchain_callbacks()},
    )
