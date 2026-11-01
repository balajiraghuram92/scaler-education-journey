# When simple tools aren't enough

## When simple tools aren't enough

This module closes with three scenarios where the plain `@tool` approach strains. Learn these as *"recognise it when it happens"*, not as something to memorise.

#### 16.1 · The database connection problem → class-based tools

The story: your agent has five tools, each opening its own database connection. Your DBA messages: *"Why is your agent opening 50 database connections per minute?"* Each tool call opens and closes a connection; multiply by concurrent users and the database drowns.

**The fix:** group related tools in a class so they share one connection.

```pseudo title="shivank2/08_class_based_tools.py"
DEFINE class InventoryTools
    ON CREATE (__init__)
        SET self.products = three products (PROD-123, PROD-456, PROD-789), each with a name, quantity and price   // shared data store; in production: a database connection

    DEFINE check_stock(product_id) as a tool
        SET product = the product with that id
        IF there is no product THEN
            RETURN "Product " + product_id + " not found"
        RETURN the name + ": " + the quantity + " units at $" + the price

    DEFINE update_stock(product_id, quantity) as a tool
        IF product_id is in self.products THEN
            SET that product's quantity = quantity
            RETURN "Updated " + product_id + " to " + quantity + " units"
        RETURN "Product " + product_id + " not found"

CREATE inventory = one InventoryTools   // one instance, shared state
CREATE agent = Agent with inventory.check_stock and inventory.update_stock
ASK agent "Check stock for PROD-123"
ASK agent "Update PROD-456 stock to 25 units, then confirm the new level"
```

> **Imported:**
> - `Agent` from `strands`: the agent that is given the two tool methods.
> - `tool` from `strands`: the decorator that turns each method into a tool.

```python reveal title="shivank2/08_class_based_tools.py"
from strands import Agent, tool

class InventoryTools:
    def __init__(self):
        # Shared resource: all tools access the same data store.
        # In production: self.db = connect_to_database()
        self.products = {
            "PROD-123": {"name": "Wireless Mouse", "quantity": 15, "price": 29.99},
            "PROD-456": {"name": "USB-C Hub", "quantity": 0, "price": 49.99},
            "PROD-789": {"name": "Mechanical Keyboard", "quantity": 8, "price": 89.99},
        }

    @tool
    def check_stock(self, product_id: str) -> str:
        """Check product stock level.

        Args:
            product_id: The product ID to check
        """
        product = self.products.get(product_id)
        if not product:
            return f"Product {product_id} not found"
        return f"{product['name']}: {product['quantity']} units at ${product['price']}"

    @tool
    def update_stock(self, product_id: str, quantity: int) -> str:
        """Update product stock quantity.

        Args:
            product_id: The product ID to update
            quantity: New quantity to set
        """
        if product_id in self.products:
            self.products[product_id]["quantity"] = quantity
            return f"Updated {product_id} to {quantity} units"
        return f"Product {product_id} not found"

# One instance, shared state, multiple tools
inventory = InventoryTools()
agent = Agent(tools=[inventory.check_stock, inventory.update_stock])

agent("Check stock for PROD-123")
agent("Update PROD-456 stock to 25 units, then confirm the new level")
```

▶ Run it

```text
python shivank2/08_class_based_tools.py
```

#### 16.2 · Slow sequential calls → async tools

If three warehouse lookups take 2 seconds each, doing them one after another costs 6 seconds. Make the tool `async` and they run in parallel.

```pseudo title="shivank2/09_async_tools.py"
DEFINE check_warehouse_inventory(product_id, warehouse) as an async tool
    WAIT 2 seconds   // simulates a slow API call
    SET data = the stock of PROD-123 and PROD-456 in the east, west and central warehouses
    SET quantity = data[warehouse][product_id], or 0 if missing
    RETURN warehouse, product_id and quantity

DEFINE async main()
    CREATE agent = Agent with the check_warehouse_inventory tool
    SET start = the current time
    SET response = WAIT for agent.invoke_async("Can we ship 100 units of PROD-123? Check all warehouses: east, west, and central.")
    SET elapsed = the current time - start
    PRINT the text of the response message
    PRINT "Total time: " + elapsed + "s (sequential would be ~6s)"

WAIT for main()   // top-level await, as in a notebook
```

> **Imported:**
> - `asyncio` Python standard library: provides `asyncio.sleep` for the simulated delay.
> - `time` Python standard library: measures how long the whole run takes.
> - `Agent` from `strands`: the agent that is given the async tool.
> - `tool` from `strands`: the decorator that turns the async function into a tool.

```python reveal title="shivank2/09_async_tools.py"
import asyncio
import time
from strands import Agent, tool

@tool
async def check_warehouse_inventory(product_id: str, warehouse: str) -> dict:
    """Check inventory at a specific warehouse.

    Args:
        product_id: Product ID to check
        warehouse: Warehouse identifier (e.g., "east", "west", "central")
    """
    # Simulate API call delay
    await asyncio.sleep(2)

    data = {
        "east":    {"PROD-123": 45, "PROD-456": 12},
        "west":    {"PROD-123": 30, "PROD-456": 0},
        "central": {"PROD-123": 60, "PROD-456": 25},
    }

    quantity = data.get(warehouse, {}).get(product_id, 0)
    return {
        "warehouse": warehouse,
        "product_id": product_id,
        "quantity": quantity
    }

async def main():
    agent = Agent(tools=[check_warehouse_inventory])
    start = time.time()
    response = await agent.invoke_async(
        "Can we ship 100 units of PROD-123? Check all warehouses: east, west, and central."
    )
    elapsed = time.time() - start
    print(response.message['content'][0]['text'])
    print(f"\nTotal time: {elapsed:.1f}s (sequential would be ~6s)")

await main()
```

▶ Run it

```text
python shivank2/09_async_tools.py
```

> **Great demo moment:**
> The printed timing is the lesson: roughly 2 seconds instead of 6. Run it yourself — you *see* concurrency instead of just reading about it. (The bare `await main()` works in a Jupyter cell; in a plain script use `asyncio.run(main())`.)

---

Capstone

Section 17

## Project — build a Travel Assistant Agent

This project deliberately mirrors Diagram 3 (the travel planner), so you finish where Module 1 began — except this time you build it yourself. It exercises every skill from both modules: custom tools, multiple tools, a pre-built tool, a system prompt, and the agentic loop.

#### The brief

Build an agent that answers: *"I'm going to Goa for 3 days next week with a budget of ₹20,000. What should I pack and what will it cost?"* — and actually reasons across weather, packing, and budget to answer it.

| Tool | Job | Skill practised |
| --- | --- | --- |
| `get_weather_forecast` | Return conditions for a city and date range | Custom tool, mock data |
| `suggest_packing_list` | Turn weather + trip length into a packing list | Tool that consumes another tool's output |
| `estimate_trip_cost` | Rough cost from city, days, travellers | Numeric logic + dict return |
| `calculator` | Budget maths | Pre-built community tool |

#### Starter code

```pseudo title="shivank3/travel_assistant.py"
DEFINE get_weather_forecast(city, days) as a tool   // mock data for now, to be swapped for a real weather API
    RETURN city, days, and the high, low and conditions for that city
DEFINE suggest_packing_list(high_c, low_c, days, conditions) as a tool
    SET items = days + 1 sets of clothes, toiletries, phone charger
    IF high_c >= 30 THEN ADD light cotton clothing, sunscreen, sunglasses and a water bottle
    IF low_c <= 15 THEN ADD warm jacket and thermal layer
    ELSE IF low_c <= 22 THEN ADD light jacket for evenings
    IF conditions mention rain or showers THEN ADD umbrella and quick-dry footwear
    IF conditions mention snow THEN ADD gloves, woollen cap and waterproof boots
    RETURN items
DEFINE estimate_trip_cost(city, days, travellers = 1) as a tool
    SET stay = the nightly rate for city x days   // default rate if the city is unknown
    SET food = 1200 x days x travellers
    SET local_travel = 800 x days
    RETURN each amount, and total = stay + food + local_travel

CREATE model = a Bedrock model, Claude Haiku 4.5
CREATE agent = Agent with the model, the three custom tools, calculator and the travel system prompt
IF this file is run directly THEN
    ASK agent "I'm going to Goa for 3 days with 2 friends. My budget is 20000 rupees. What should I pack, and does it fit my budget?"
    PRINT the answer
```

> **Imported:**
> - `Agent` from `strands`: the agent that holds the model and the tools.
> - `tool` from `strands`: the decorator that makes each function a tool.
> - `BedrockModel` from `strands.models.bedrock`: the model object that calls Claude on Amazon Bedrock.
> - `calculator` from `strands_tools`: a ready-made tool for the budget maths.

```python reveal title="shivank3/travel_assistant.py"
"""Capstone: Travel Assistant Agent (Modules 1 & 2)."""

from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from strands_tools import calculator

@tool
def get_weather_forecast(city: str, days: int) -> dict:
    """Get the weather forecast for a city over a number of days.

    Args:
        city: Destination city name (e.g., "Goa", "Bangalore")
        days: Number of days in the trip
    """
    # Mock data — replace with a real weather API to go further
    forecasts = {
        "goa":       {"high_c": 32, "low_c": 26, "conditions": "humid, occasional showers"},
        "bangalore": {"high_c": 27, "low_c": 18, "conditions": "mild, light evening rain"},
        "jaipur":    {"high_c": 38, "low_c": 25, "conditions": "hot and dry"},
        "manali":    {"high_c": 14, "low_c": 3,  "conditions": "cold, chance of snow"},
    }
    data = forecasts.get(city.lower(), {"high_c": 28, "low_c": 20, "conditions": "moderate"})
    return {"city": city, "days": days, **data}

@tool
def suggest_packing_list(high_c: int, low_c: int, days: int, conditions: str) -> list:
    """Suggest what to pack based on temperatures, trip length and conditions.

    Args:
        high_c: Daytime high in Celsius
        low_c: Night-time low in Celsius
        days: Number of days in the trip
        conditions: Short description of expected weather
    """
    items = [f"{days + 1} sets of clothes", "toiletries", "phone charger"]

    if high_c >= 30:
        items += ["light cotton clothing", "sunscreen", "sunglasses", "reusable water bottle"]
    if low_c <= 15:
        items += ["warm jacket", "thermal layer"]
    elif low_c <= 22:
        items += ["light jacket for evenings"]
    if "rain" in conditions.lower() or "shower" in conditions.lower():
        items += ["compact umbrella", "quick-dry footwear"]
    if "snow" in conditions.lower():
        items += ["gloves", "woollen cap", "waterproof boots"]

    return items

@tool
def estimate_trip_cost(city: str, days: int, travellers: int = 1) -> dict:
    """Estimate the cost of a trip in Indian rupees.

    Args:
        city: Destination city
        days: Number of days
        travellers: Number of people travelling (default: 1)
    """
    per_night = {"goa": 3500, "bangalore": 3000, "jaipur": 2500, "manali": 2800}
    stay = per_night.get(city.lower(), 3000) * days
    food = 1200 * days * travellers
    local_travel = 800 * days
    total = stay + food + local_travel

    return {
        "city": city,
        "days": days,
        "travellers": travellers,
        "stay_inr": stay,
        "food_inr": food,
        "local_travel_inr": local_travel,
        "total_inr": total,
    }

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")

agent = Agent(
    model=model,
    tools=[get_weather_forecast, suggest_packing_list, estimate_trip_cost, calculator],
    system_prompt=(
        "You are a practical travel assistant. "
        "When asked about a trip: check the weather first, then suggest what to pack "
        "based on that weather, then estimate the cost. "
        "Always say whether the trip fits the user's budget, and keep advice concise."
    ),
)

if __name__ == "__main__":
    response = agent(
        "I'm going to Goa for 3 days with 2 friends. My budget is 20000 rupees. "
        "What should I pack, and does it fit my budget?"
    )
    print(response)
```

```pseudo title="shivank3/travel_assistant.py"
RUN python shivank3/travel_assistant.py   // asks the Goa question that is written inside the file
RUN python shivank3/travel_assistant.py "I'm going to Manali for 4 days, budget 15000"   // the file never reads command-line arguments, so this runs the same Goa question
```

```python reveal
python shivank3/travel_assistant.py

# or ask your own question:
python shivank3/travel_assistant.py "I'm going to Manali for 4 days, budget 15000"
```

▶ Run it

#### What to observe together

Notice that the agent calls `get_weather_forecast` **first**, then feeds those numbers into `suggest_packing_list`, then prices the trip and compares against the budget. Nobody wrote that sequence — the agentic loop worked it out. That is Diagram 9, running in your own terminal.

#### Extension challenges

- **Easy** — add a `get_visa_requirements(country)` tool and ask about an international trip.
- **Medium** — replace the mock weather with a real API call using `requests` (this is exactly the pattern from Section 10).
- **Medium** — regroup the three tools into a `TravelTools` class with shared state, per Section 16.1.
- **Harder** — make the weather and cost lookups `async` so a multi-city comparison runs in parallel (Section 16.2).
- **Harder** — add `file_write` from `strands_tools` and have the agent save an itinerary to disk.

> **How to know you have really got it:**
> You have genuinely understood these two modules if you can: (1) explain why the docstring matters, (2) add a fourth tool without help, (3) predict which tools the agent will call for a given question, and (4) debug a retired-model error on your own.

Section 17b

## Every command in one place

Copy-paste reference. Run all of these from the project root — the folder containing `config.py`.

#### Setup (once)

```pseudo title="setup.sh and 00_check_setup.py"
RUN ./setup.sh   // macOS / Linux (Windows: setup.bat)
RUN source .venv/bin/activate
SET AWS_DEFAULT_REGION = us-east-1
RUN python 00_check_setup.py   // verifies everything and makes a real model call
```

```python reveal
./setup.sh                       # macOS / Linux  (Windows: setup.bat)
source .venv/bin/activate
export AWS_DEFAULT_REGION=us-east-1
python 00_check_setup.py         # verifies everything, makes a real model call
```

▶ Run it

#### Every example, in learning order

```pseudo title="every example script"
// Module 1 · first agents
RUN python shivank1/01_hello_world_agent.py   // simplest agent, no tools
RUN python shivank1/02_hello_world_langgraph.py   // with a tool: watch the loop
// Module 2 · tools
RUN python shivank2/01_function_to_tool.py   // the core idea: @tool
RUN python shivank2/02_tip_calculator.py   // first useful tool agent
RUN python shivank2/03_multi_tool_sales.py   // three tools, the agent picks the order
RUN python shivank2/04_custom_tool_inventory.py   // build your own tool
RUN python shivank2/05_prebuilt_tools.py   // community tools and a system prompt
RUN python shivank2/06_multi_prebuilt_tools.py   // combining several tools
RUN python shivank2/07_use_aws.py   // one tool, many AWS services
RUN python shivank2/08_class_based_tools.py   // shared-resource pattern
RUN python shivank2/09_async_tools.py   // parallel tools: 2s, not 6s
// Module 3 · capstone
RUN python shivank3/travel_assistant.py
```

```python reveal
# ---- Module 1 · first agents ----
python shivank1/01_hello_world_agent.py        # simplest agent, no tools
python shivank1/02_hello_world_langgraph.py    # with a tool — watch the loop

# ---- Module 2 · tools ----
python shivank2/01_function_to_tool.py         # THE core idea: @tool
python shivank2/02_tip_calculator.py           # first useful tool agent
python shivank2/03_multi_tool_sales.py         # 3 tools, agent picks the order
python shivank2/04_custom_tool_inventory.py    # build your own tool
python shivank2/05_prebuilt_tools.py           # community tools + system prompt
python shivank2/06_multi_prebuilt_tools.py     # combining several tools
python shivank2/07_use_aws.py                  # one tool, many AWS services
python shivank2/08_class_based_tools.py        # shared-resource pattern
python shivank2/09_async_tools.py              # parallel tools: 2s not 6s

# ---- Module 3 · capstone ----
python shivank3/travel_assistant.py
```

▶ Run it

#### Helpers

```pseudo title="troubleshooting commands"
RUN python 00_check_setup.py   // run whenever something breaks
RUN python 01_list_models.py   // when a model is retired, pick a new one
RUN aws sts get-caller-identity   // are my credentials alive?
RUN env | grep AWS   // what credentials are actually set?
```

```python reveal
python 00_check_setup.py     # run whenever something breaks
python 01_list_models.py     # when a model is retired, pick a new one
aws sts get-caller-identity  # are my credentials alive?
env | grep AWS               # what credentials are actually set?
```

▶ Run it

Section 18

## Study plan & troubleshooting

#### Suggested 3-hour study plan

| Time | Segment | Notes |
| --- | --- | --- |
| 0:00–0:20 | AWS setup (Section 0) | Do not skip. Run `python 00_check_setup.py` and wait for all six OK lines. |
| 0:20–0:50 | Concepts: RAG → agents → the loop | Diagrams 1, 2, 3, 4 and 9. Keep moving — you will revisit them. |
| 0:50–1:15 | Hello World agents | Both files. Unpack the tool-call output line by line. |
| 1:15–1:25 | Break |  |
| 1:25–2:00 | Function → tool → tip calculator | Do the docstring experiment here. |
| 2:00–2:30 | Multi-tool + pre-built + use_aws | Read-only AWS calls only. |
| 2:30–3:00 | Capstone project | Build the skeleton now, finish it in your own time. |

#### Troubleshooting — keep this open while you work

| Symptom | Cause & fix |
| --- | --- |
| `ResourceNotFoundException … end of its life` / `marked by provider as Legacy` | Retired model. Run `python 01_list_models.py`, pick a live one, change `MODEL_ID` in `config.py`. |
| `AccessDeniedException` | Model not enabled in Bedrock → Model access, or wrong region. Check both. |
| `InvalidClientTokenId` | Credentials stale or deleted. Create a new access key and re-run `aws configure`. |
| `ModuleNotFoundError: No module named 'strands'` | Wrong Python. Activate the venv; in Jupyter, switch the kernel. |
| Notebook cell stuck on `[*]` | A tool is waiting for consent. Type `y` at the hidden prompt, or set `BYPASS_TOOL_CONSENT="true"` in an earlier cell. |
| Terminal shows `quote>` or `:` and seems frozen | `quote>` = unclosed quote, press Ctrl+C. `:` = the AWS CLI pager, press `q`. Set `export AWS_PAGER=""` to stop it. |
| Agent ignores your tool | Weak docstring or missing type hints. Rewrite the description to say plainly when it should be used. |
| `ModuleNotFoundError: No module named 'config'` | You ran from inside a subfolder. Run from the project root: `python shivank1/01_hello_world_agent.py`. |
| Worked yesterday, fails today | Almost always expired SSO credentials. Paste a fresh block, then `python 00_check_setup.py`. |

#### The five sentences to remember

1. RAG gives a model better *information*; tools give it the ability to *act*.
2. An agent is a loop: reason → call a tool → read the result → repeat until done.
3. A tool is just a Python function plus a decorator, type hints, and a good docstring.
4. The docstring is the model's user manual — write it for the model, not for yourself.
5. Build small, single-purpose tools; the agent handles the sequencing.

---

Future with Shivank · AI Agents on AWS masterclass · Strands SDK + Amazon Bedrock · us-east-1
