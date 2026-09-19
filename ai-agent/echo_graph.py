from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentGraph(TypedDict):
    input_txt: str
    output_txt: str


def node(State: AgentGraph) -> dict:
    return {"output_txt": f"graph says: {State['input_txt']}"}


builder = StateGraph(AgentGraph)
builder.add_node("root_step", node)
builder.add_edge(START, "root_step")
builder.add_edge("root_step", END)

agent_graph = builder.compile()   