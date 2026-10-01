from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class AgentGraph(TypedDict):
    input_txt: str
    output_txt: str


def node(state: AgentGraph) -> dict:
    return {"output_txt": f"graph says: {state['input_txt']}"}


builder = StateGraph(AgentGraph)
builder.add_node("root_step", node)
builder.add_edge(START, "root_step")
builder.add_edge("root_step", END)

# Langfuse callbacks are attached per invocation (see routers/graph_demo.py),
# so importing this module creates no tracing client.
agent_graph = builder.compile()
