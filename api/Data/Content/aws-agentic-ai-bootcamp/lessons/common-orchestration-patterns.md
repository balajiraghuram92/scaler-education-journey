# Common orchestration patterns

## 4.7 Common orchestration patterns

Supervisor–worker is the pattern most organisations use, but it isn't the only one. Two more solve very different problems: swarms and graphs.

Each uses the communication building blocks you just learned, arranged for a specific kind of problem. A swarm lets agents decide who goes next; a graph makes you decide, in code, ahead of time. We cover the swarm (notebook 04) before the graph (notebook 03) because the graph is easiest to understand by contrast; you can run the two notebooks in either order.

#### Swarm: agents hand work to each other

A **swarm** builds a whole system out of collaborative communication. The hard part of collaboration is coordination: who talks to whom, when, and how do you stop agents talking in circles? A swarm answers with **handoffs**: agents explicitly pass control to each other.

> **Think of it like this:**
> A game-design team building a stealth mission in an abandoned space station. The level designer creates the floor plan and a rough 3D **blockout**. In playtesting, the game designer finds players get lost, so it goes back to the level designer, who adds landmarks and lighting. Then the narrative designer objects: bright lighting contradicts the story of a creepy, abandoned station. The level designer switches to dim emergency lights and environmental storytelling. Now the difficulty balancer finds the level too easy with clearer navigation, so back to the level designer for tougher enemy placement, without removing the visual cues. The path loops and branches based on what each specialist finds. Nobody could have predicted it up front.

In a swarm you'd have four agents, `level_designer`, `game_designer`, `narrative_designer` and `difficulty_balancer`, each with its own expertise. There's no supervisor and no fixed sequence. When an agent finishes its part, it decides who should go next and hands off the task with context about what's been done.

{{diagram:1}}

*No boss, just handoffs. Any agent can pass control to any other. Whoever picks up the task receives a briefing built by the swarm: the handoff message, the original task, who has worked on it, and any notes passed along.*

##### Run the notebook: `04_swarm_pattern.ipynb`

After the usual install and model cells:

```python title="cell 3: imports and handoff logging"
import logging

from strands import Agent
from strands.multiagent import Swarm

# Show each handoff as it happens
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()])
```

The two logging lines switch on Strands' multi-agent debug messages, so you can watch every handoff live.

```python title="cell 4: specialist agents"
level_designer = Agent(
    name="level_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Level Designer in a game design swarm.
Your role is to create level layouts, environments, and visual elements.
Focus ONLY on layout and visual design. Do NOT write narrative or balance difficulty.
After completing your layout, hand off to narrative_designer for story elements
and difficulty_balancer for gameplay tuning.
When receiving feedback from other agents, revise your design accordingly.""",
)

game_designer = Agent(
    name="game_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Game Designer in a game design swarm.
Your role is to playtest designs for fun, usability, and player confusion.
Focus ONLY on gameplay feel and player experience. Do NOT design layouts or write narrative.
When you find issues, hand off to the appropriate specialist to fix them.
When the design is ready, give the final summary and do not hand off.""",
)

narrative_designer = Agent(
    name="narrative_designer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Narrative Designer in a game design swarm.
Your role is to create story elements, character backstories, and atmospheric details.
Focus ONLY on narrative. Do NOT redesign layouts or adjust difficulty.
After adding narrative elements, hand off to difficulty_balancer for balance review
or game_designer for playtesting feedback.""",
)

difficulty_balancer = Agent(
    name="difficulty_balancer",
    model=model,
    callback_handler=None,
    system_prompt="""You are a Difficulty Balancer in a game design swarm.
Your role is to evaluate and tune difficulty progression, enemy placement, and pacing.
Focus ONLY on balance. Do NOT redesign layouts or write narrative.
When you find layout or narrative issues, hand off to the appropriate agent.
After balancing, hand off to game_designer for a final playtest review.""",
)
```

Read the prompts closely: each one says what the agent does, what it must *not* do ("Do NOT write narrative"), and whom to hand off to. The game designer's prompt contains the exit: *"When the design is ready, give the final summary and do not hand off."* A swarm finishes when an agent completes its turn without handing off.

##### Create the swarm

The swarm gives every agent a `handoff_to_agent` tool and a shared view of the work so far. For example, the game designer might call:

```python title="a handoff, as the model calls it"
handoff_to_agent(
    agent_name="difficulty_balancer",
    message="Patrol patterns too predictable - need more variation",
)
```

```python title="cell 5"
swarm = Swarm(
    [level_designer, game_designer, narrative_designer, difficulty_balancer],
    entry_point=level_designer,
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=1200.0,
    node_timeout=300.0,
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3,
)
print("✓ Swarm created")
```

| Setting | Value | What it protects against |
| --- | --- | --- |
| `entry_point` | `level_designer` | Which agent starts. A layout has to exist before anyone can review it. |
| `max_handoffs` | 20 | Caps how many times control can be passed. |
| `max_iterations` | 20 | Caps the total number of agent turns. Without these limits, agents could loop forever. (In the current Strands version both are counted as completed agent turns, so they behave alike; setting both is belt and braces.) |
| `execution_timeout` | 1200.0 s | Wall-clock cap for the whole swarm (20 minutes). |
| `node_timeout` | 300.0 s | Wall-clock cap for any single agent's turn (5 minutes). |
| `repetitive_handoff_detection_window` | 8 | **Ping-pong**: two agents bouncing the task back and forth without progress. The swarm looks at the last 8 turns; if fewer than 3 different agents appear, it stops. So if the level and narrative designers trade the task 8 times without anyone else, the loop is detected and the swarm ends. |
| `repetitive_handoff_min_unique_agents` | 3 |  |

##### Run the swarm (takes a few minutes)

```python title="cell 6"
result = swarm("""Design a stealth mission level in an abandoned space station.
The level needs to support multiple playstyles (aggressive stealth, patient stealth, and ghost runs).
Include at least 3 distinct zones with different difficulty levels,
narrative elements that explain why the station was abandoned,
and ensure the difficulty curve is appropriate for mid-game players.""")

print("=" * 80)
print("HANDOFF CHAIN:")
for node in result.node_history:
    print(f"  → {node.node_id}")
print(f"\nStatus: {result.status} | iterations: {result.execution_count} | time: {result.execution_time / 1000:.0f}s")
```

```text title="outputillustrative; your path will differ"
DEBUG | strands.multiagent.swarm | current_node=<level_designer>, iteration=<1> | executing node
DEBUG | strands.multiagent.swarm | from_node=<level_designer>, to_node=<narrative_designer> | handoff detected
DEBUG | strands.multiagent.swarm | current_node=<narrative_designer>, iteration=<2> | executing node
DEBUG | strands.multiagent.swarm | from_node=<narrative_designer>, to_node=<difficulty_balancer> | handoff detected
DEBUG | strands.multiagent.swarm | current_node=<difficulty_balancer>, iteration=<3> | executing node
DEBUG | strands.multiagent.swarm | from_node=<difficulty_balancer>, to_node=<game_designer> | handoff detected
DEBUG | strands.multiagent.swarm | current_node=<game_designer>, iteration=<4> | executing node
DEBUG | strands.multiagent.swarm | from_node=<game_designer>, to_node=<level_designer> | handoff detected
...
DEBUG | strands.multiagent.swarm | node=<game_designer> | no handoff occurred, marking swarm as complete
DEBUG | strands.multiagent.swarm | status=<Status.COMPLETED> | swarm execution completed
DEBUG | strands.multiagent.swarm | node_history_length=<11>, time=<486.46>s | metrics
================================================================================
HANDOFF CHAIN:
  → level_designer
  → narrative_designer
  → difficulty_balancer
  → game_designer
  → level_designer
  → game_designer
  → …
  → game_designer

Status: Status.COMPLETED | iterations: 11 | time: 486s
```

Read the chain as a story. The level designer drew the layout and handed off to the narrative designer for story elements, who added the backstory and passed it to the difficulty balancer for tuning, who handed off to the game designer for playtesting. The game designer found navigation problems in zone 2 and sent it back to the level designer. That back-and-forth continued for 11 turns until the game designer approved the final design. **Nobody programmed this sequence.** The agents worked it out from what needed to happen next.

```python title="cell 7: show the final design"
from IPython.display import Markdown, display

last_node = result.node_history[-1].node_id
display(Markdown(str(result.results[last_node].result)))
```

`result.node_history` lists every turn in order; the last entry is the agent that finished (usually the game designer with its final summary). `result.results` maps each agent's name to its last output, which this cell renders as Markdown.

##### How a handoff works under the hood

Handoffs happen through tool calls. When you create a `Swarm`, every agent automatically gets a `handoff_to_agent` tool, and the swarm keeps a shared record of the run. Say the game designer finishes playtesting and finds enemy patrols are too predictable. That's a difficulty problem, not a playtesting problem, so it needs someone who can tune the challenge. When its turn began, the swarm gave the game designer a formatted briefing that includes:

1. 1 The handoff message What the previous agent said it needs, for example "Add landmarks in zone 2".
2. 2 The original task
3. 3 The agents who have worked on it so far For example `level_designer → game_designer`.
4. 4 What previous agents contributed As "shared knowledge from previous agents": whatever notes an agent chose to pass in the handoff's optional `context` argument.
5. 5 The other available agents By name, plus each one's `description` if you gave it one. The game designer reads: the level designer creates layouts and visuals; the narrative designer creates story and atmosphere; the difficulty balancer tunes difficulty, enemy placement and pacing.

The patrol problem matches the difficulty balancer, so the game designer calls `handoff_to_agent(agent_name="difficulty_balancer", message="Patrol patterns too predictable - need more variation")`. Now the difficulty balancer is in control and receives the same formatted context, including what the game designer found. The LLM makes each routing decision by matching the problem to what each agent does.

> **Write handoffs like a good shift-change note:**
> Each agent's own conversation is reset before its turn, so a returning level designer doesn't automatically see its earlier layout. Knowledge travels in the handoff `message` (and optional `context`). Prompting agents to summarise what they did and what's needed when they hand off makes swarms work much better.

> **Tip: give swarm agents a description:**
> The lab's agents rely on their names and prompts. Adding `description="Tunes difficulty, enemy placement and pacing"` to each `Agent(...)` puts that text in every teammate's list of available agents, which makes handoff choices more reliable.

Try it

##### Run a swarm, one turn at a time

Swarm log

Briefing the next agent receives

Last 8 turns: unique agents

**Good run:**

1. **level_designer:** Drafted 3 zones: docking bay (easy), reactor core (medium), command deck (hard). Handoff to `narrative_designer`: "Add story to these zones"
2. **narrative_designer:** Station abandoned after a reactor leak; crew logs scattered as environmental storytelling. Handoff to `difficulty_balancer`: "Check pacing across zones"
3. **difficulty_balancer:** Command deck patrols too sparse for mid-game; added two patrol routes. Handoff to `game_designer`: "Playtest, please"
4. **game_designer:** Players get lost in the reactor core: not enough visual cues. Handoff to `level_designer`: "Add landmarks in zone 2"
5. **level_designer:** Added bright signage and landmarks in zone 2. Handoff to `narrative_designer`: "Does the new lighting fit the story?"
6. **narrative_designer:** Bright signs break the abandoned mood. Use flickering emergency lights instead. Handoff to `level_designer`: "Swap to dim emergency lights"
7. **level_designer:** Replaced with dim emergency lights and floor markings. Handoff to `difficulty_balancer`: "Re-check difficulty with clearer navigation"
8. **difficulty_balancer:** Now too easy; added a roaming drone in zone 2 without blocking the cues. Handoff to `game_designer`: "Final review"
9. **game_designer:** Fun, readable, good difficulty curve. Final summary written. The log then shows: node=`<game_designer>` | no handoff occurred, marking swarm as complete. Status.COMPLETED after 9 turns. Nobody scripted this order.

**Ping-pong run:** two turns alternate until the detector stops them. `level_designer` makes zone 2 brighter (*Made zone 2 brighter so players don't get lost.*) and hands off with "Check lighting vs story"; `narrative_designer` replies (*Too bright for an abandoned station. Make it darker.*) and hands off with "Darken zone 2". After eight turns the log shows: **Stopped:** Repetitive handoff: 2 unique nodes out of 8 recent iterations. The detection window caught the ping-pong.

> **Use a swarm for:**
> Creative and iterative work where you can't predict the path up front. Sometimes the layout passes every reviewer first time; sometimes it bounces around as new problems appear. You define the agents and their strengths; they work out who handles each issue.

> **Don't use one when:**
> You need a fixed sequence where certain checks always happen in a specific order. That's the graph pattern's job.

#### Graph: you define the paths

The **graph pattern** is built on a **directed graph**: data flows along defined paths from one node to the next. There are two flavours:

{{diagram:2}}

*Forward-only vs loops. Production workflows mostly use DAGs, so that's the focus here. (Strands also supports cyclic graphs, with safety limits such as a cap on total node executions and timeouts.)*

"Isn't that what a swarm does?" The key difference: **in a swarm, agents decide the path; in a graph, you define the paths up front.** Before the example, the building blocks:

##### Nodes

Anything that processes data. In Strands a node can be a single agent (like a fraud-detection agent), a swarm of agents, another graph (graphs can be nested), or custom business logic: your own deterministic code wrapped as a node.

##### Edges

The connections. An edge says "when node A finishes, pass its output to node B". Edges can carry **conditions**, for example "only follow this edge if the order is over $1,000".

##### Dependencies

If node B depends on node A, A must finish before B starts. The graph manages this and runs nodes in the right order. When several arrows lead into one node (like inventory check below), it runs as soon as one incoming arrow fires.

##### The example: processing e-commerce orders

Orders arrive all day. Some are small purchases from regular customers; some are big orders from brand-new accounts; some ship somewhere that doesn't match the billing address. You can't treat them all the same way.

You *could* use supervisor–worker: the supervisor reads each order and decides where to send it. It works, until your payment processor asks, *"How do you guarantee high-value orders always get fraud review?"* With a supervisor, the routing happens inside the LLM's reasoning. You can log it, but the decision logic isn't explicit in your code.

A graph makes the routing explicit. The risk analyser runs first; high-value orders go to manual review; suspicious ones go to fraud detection; clean, low-risk orders go straight to the inventory check. The decision tree is visible in your code, and anyone can see exactly what happens to each kind of order.

{{diagram:3}}

*Every path drawn in advance. Three ways in, one meeting point at inventory, two possible endings. The labels on the edges are the exact words the routing code looks for. The dashed box isn't a node: low-risk orders go straight from risk analysis to the inventory check.*

1. 1 High-value orders go to manual review first
2. 2 Suspicious orders go to advanced fraud detection Red flags such as a billing and shipping mismatch, or a brand-new account placing a large order.
3. 3 Low-risk orders from trusted customers skip the checks They go straight to inventory.
4. 4 All three paths meet at the inventory check In stock: shipping generates a label and the package goes out. Out of stock: refund processing notifies the customer and returns the payment. Every order ends in one of these two states.

**Directed** means arrows point one way: from the risk analyser to fraud check, never backwards. **Acyclic** means no loops: you can't go risk analyser → fraud check → inventory → back to risk analyser, which could cycle forever. That structure guarantees every order eventually reaches an end state, shipped or refunded.

That's why graphs are great for **compliance and auditability**. When your payment processor asks about fraud prevention, you point at the graph. The logic lives in code, not hidden in LLM reasoning. A large order from a new customer always follows the same path; it doesn't vary with how an LLM reads the situation that day.

> **So where does the LLM fit?:**
> The graph defines the *flow*; each node is still an agent that uses an LLM for its *task*. The risk analyser understands the order in natural language, the fraud agent reasons about suspicious patterns, the inventory agent interprets stock data. You define the routing; the LLMs do the reasoning at each step.

##### Run the notebook: `03_graph_pattern.ipynb`

After the usual install and model cells:

```python title="cell 3"
from strands import Agent
from strands.multiagent import GraphBuilder
```

The two "decision" agents end their answer with a fixed line (`RISK_CATEGORY: ...`, `STOCK_STATUS: ...`). The routing functions read only that line, so an explanation that merely *mentions* another category can't send the order down the wrong path.

```python title="cell 4: specialised agents"
risk_analyzer = Agent(
    name="risk_analyzer",
    model=model,
    callback_handler=None,
    system_prompt="""Analyze the order's risk level and pick exactly ONE category:
- HIGH_VALUE: orders over $1,000
- SUSPICIOUS: mismatched billing/shipping country, brand-new account with a large order, or known fraud patterns
- LOW_RISK: regular orders from trusted customers
If more than one applies, SUSPICIOUS wins over HIGH_VALUE.
Give a one-paragraph explanation, then finish with a final line in exactly this format:
RISK_CATEGORY: <HIGH_VALUE|SUSPICIOUS|LOW_RISK>""",
)

manual_review_agent = Agent(
    name="manual_review_agent",
    model=model,
    callback_handler=None,
    system_prompt="Review high-value orders. Verify customer identity, check order history, and approve or flag for further review.",
)

fraud_detection_agent = Agent(
    name="fraud_detection_agent",
    model=model,
    callback_handler=None,
    system_prompt="Run fraud detection on suspicious orders: known fraud patterns, velocity checks, and device fingerprinting. Decide whether to proceed.",
)

inventory_agent = Agent(
    name="inventory_agent",
    model=model,
    callback_handler=None,
    system_prompt="""Check inventory for the order items. Assume laptops, books and phones are in stock and
anything described as 'limited edition' or 'pre-order' is out of stock.
Explain briefly, then finish with a final line in exactly this format:
STOCK_STATUS: <IN_STOCK|OUT_OF_STOCK>""",
)

shipping_agent = Agent(
    name="shipping_agent",
    model=model,
    callback_handler=None,
    system_prompt="Generate a shipping label and process the shipment. Confirm a tracking number and estimated delivery date.",
)

refund_agent = Agent(
    name="refund_agent",
    model=model,
    callback_handler=None,
    system_prompt="Process a refund for out-of-stock items. Notify the customer and initiate the payment reversal.",
)

print("✓ All agents created")
```

> **Two lab conveniences:**
> The risk rules use dollars ($1,000) to match the sample orders. And the inventory agent *pretends* to check stock using a simple rule (laptops, books and phones in stock; "limited edition" and "pre-order" out of stock). In a real system that node would call your inventory database as a tool.

##### Routing conditions

Each condition reads the previous node's output and returns `True` or `False`. The logic is plain Python, not hidden inside model reasoning.

```python title="cell 5"
import re

def decision(state, node_id: str, label: str) -> str:
    """Return the value of the final 'LABEL: VALUE' line written by a node."""
    text = str(state.results.get(node_id, ""))
    matches = re.findall(rf"{label}\s*:\s*([A-Z_]+)", text.upper())
    return matches[-1] if matches else ""

def is_high_value(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "HIGH_VALUE"

def is_suspicious(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "SUSPICIOUS"

def is_low_risk(state):
    return decision(state, "risk_analysis", "RISK_CATEGORY") == "LOW_RISK"

def is_in_stock(state):
    return decision(state, "inventory_check", "STOCK_STATUS") == "IN_STOCK"

def is_out_of_stock(state):
    return decision(state, "inventory_check", "STOCK_STATUS") == "OUT_OF_STOCK"

print("✓ Routing conditions defined")
```

1. a `state.results` The graph's record of every node's output so far, keyed by node ID. `str(...)` turns a node's result into its text.
2. b The **regular expression** `RISK_CATEGORY\s*:\s*([A-Z_]+)` finds "RISK_CATEGORY", optional spaces, a colon, optional spaces, then captures a word in capitals and underscores. `.upper()` makes it case-insensitive, and `matches[-1]` takes the *last* match, the required final line, so earlier mentions in the explanation are ignored.
3. c Five tiny conditions One per edge that needs a decision. Each is a one-line, testable Python function.

##### Build the graph

```python title="cell 6"
builder = GraphBuilder()

# Nodes
builder.add_node(risk_analyzer, "risk_analysis")
builder.add_node(manual_review_agent, "manual_review")
builder.add_node(fraud_detection_agent, "fraud_check")
builder.add_node(inventory_agent, "inventory_check")
builder.add_node(shipping_agent, "shipping")
builder.add_node(refund_agent, "refund")

# Conditional edges out of risk analysis
builder.add_edge("risk_analysis", "manual_review", condition=is_high_value)
builder.add_edge("risk_analysis", "fraud_check", condition=is_suspicious)
builder.add_edge("risk_analysis", "inventory_check", condition=is_low_risk)

# Review / fraud check → inventory
builder.add_edge("manual_review", "inventory_check")
builder.add_edge("fraud_check", "inventory_check")

# Inventory → ship or refund
builder.add_edge("inventory_check", "shipping", condition=is_in_stock)
builder.add_edge("inventory_check", "refund", condition=is_out_of_stock)

builder.set_entry_point("risk_analysis")
graph = builder.build()
print("✓ Graph built")

def show_path(result):
    path = " → ".join(node.node_id for node in result.execution_order)
    print(f"Status: {result.status}\nPath:   {path}")
    last = result.execution_order[-1].node_id
    print(f"\nFinal step ({last}):\n{result.results[last].result}")
```

```text title="output"
UserWarning: … no max_node_executions or execution_timeout set …
✓ Graph built
```

The warning is expected. Strands is reminding you that this graph has no overall execution limit; for a forward-only graph like this one that's fine, because every run ends at shipping or refund. For cyclic graphs, set limits with `builder.set_max_node_executions(...)` or an execution timeout.

`add_node(agent, "node_id")` registers each agent under a short ID. `add_edge(from, to, condition=...)` draws an arrow; with a condition, the arrow is only followed when the function returns `True`. Edges without a condition are always followed. `set_entry_point` says where every run starts, and `build()` validates the setup (at least one node, a valid entry point) and returns a runnable graph. `show_path` prints the route an order took, using `result.execution_order`, and the last node's output.

##### Process orders: each one takes a different path

```python title="cell 7"
# High value → manual review → inventory → shipping
result = graph("Order #12345: $1,500 laptop from an existing customer with 3 previous orders; billing and shipping address match")
show_path(result)
```

```text title="outputillustrative"
Status: Status.COMPLETED
Path:   risk_analysis → manual_review → inventory_check → shipping

Final step (shipping):
Shipping label generated for Order #12345 (1 × laptop). Tracking number: …
Estimated delivery: 3–5 business days.
```

```python title="cell 8"
# Low risk → inventory → shipping
result = graph("Order #67890: $45 book from a returning customer with 50+ previous orders")
show_path(result)
```

```text title="outputillustrative"
Status: Status.COMPLETED
Path:   risk_analysis → inventory_check → shipping
```

```python title="cell 9"
# Suspicious → fraud check → inventory → refund (limited edition is out of stock)
result = graph(
    "Order #11111: $800 limited edition headphones, account created 5 minutes ago, "
    "shipping to a different country than the billing address"
)
show_path(result)
```

```text title="outputillustrative"
Status: Status.COMPLETED
Path:   risk_analysis → fraud_check → inventory_check → refund

Final step (refund):
Refund initiated for Order #11111: limited edition headphones are out of stock. The customer has been notified …
```

Same graph, three orders, three different paths, and each path is fully explained by the edges you wrote. Run the same order again and it takes the same path.

Try it

##### Send an order through the graph

Order value = $1,500 1500

Item (laptop / book / phone / limited edition headphones / pre-order game console)

on Brand-new account

on Shipping country differs from billing

Set up an order, then process it. The path lights up in the diagram above.

> `risk_analysis` ends with `RISK_CATEGORY: <category>` (<reason>).
> `inventory_check` ends with `STOCK_STATUS: <IN_STOCK or OUT_OF_STOCK>`. Limited edition and pre-order items are out of stock in this lab.
> **Path:** <nodes in order, joined with →>
> Run it again and you get exactly the same path: the routing is code, not a judgement call.

Possible reasons shown in the output:

- Brand-new account with a large order, or shipping country differs from billing (both marked SUSPICIOUS)
- Order over $1,000 (HIGH_VALUE)
- Regular order, no red flags (LOW_RISK)
- Also over $1,000, but SUSPICIOUS wins (when an order is both suspicious and over $1,000)

Use graphs wherever you have an established procedure: e-commerce order processing, compliance workflows, approval chains, content moderation, or anywhere you must prove that certain checks always happen in a certain order. Don't use one when the path can't be predicted up front; that's a swarm's job.

#### Choosing a pattern

| Pattern | Who decides the path? | Best for | Trade-off |
| --- | --- | --- | --- |
| Supervisor–worker | The supervisor agent | Centralised coordination with one synthesised answer; parallel research | Supervisor is a bottleneck and a single point of failure |
| Agent as tool | The orchestrator picks from available tools, and stays in control | Reusable agents across different systems; simple delegation | Agents only communicate through the orchestrator; nested calls add latency |
| Swarm | The agents, through handoffs | Creative or iterative work where the path can't be predicted | Harder to debug; the order of work varies between runs |
| Graph (DAG) | You, in code (conditional edges) | Fixed, auditable procedures and compliance workflows | Every possible path must be defined up front |

> **Patterns combine:**
> Most production systems mix them. A supervisor might coordinate workers that run in parallel; a graph node might itself be a swarm; a specialist used as a tool might be a small graph. Match the pattern to your constraints, one layer at a time.
