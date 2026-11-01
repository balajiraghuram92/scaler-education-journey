# Building custom tools

## 2.4 Building custom tools

When no community tool fits, you build your own: an internal API only your company uses, a proprietary database with its own business rules, or something nobody has built yet.

Say you run an online store, and customers ask "Is product X in stock?" all day. You need a tool that checks your inventory:

```pseudo title="01_building_tools.ipynb: inventory checker"
DEFINE check_inventory(product_id)   // @tool: the model can read the docstring and call it
    SET inventory = a dictionary: PROD-123 has 15, PROD-456 has 0, PROD-789 has 8
    SET quantity = inventory value for product_id, or 0 if the ID is unknown
    IF quantity > 0 THEN
        RETURN "Product is in stock. We have quantity units available."
    RETURN "Product is currently out of stock."

CREATE agent = Agent(model, tools = [check_inventory])
// all four questions below should lead to check_inventory
ASK agent: "Is PROD-123 in stock?"
ASK agent: "Do we have PROD-456 available?"
ASK agent: "Check inventory for PROD-789"
ASK agent: "Can I order PROD-123 right now?"
```

```python reveal title="01_building_tools.ipynb: inventory checker"
@tool
def check_inventory(product_id: str) -> str:
    """Check if a product is in stock.

    Args:
        product_id: The product ID to check (e.g., "PROD-123")
    """
    inventory = {"PROD-123": 15, "PROD-456": 0, "PROD-789": 8}
    quantity = inventory.get(product_id, 0)

    if quantity > 0:
        return f"Product {product_id} is in stock. We have {quantity} units available."
    return f"Product {product_id} is currently out of stock."

agent = Agent(model=model, tools=[check_inventory])

# All of these work — the agent understands intent, not just keywords
agent("Is PROD-123 in stock?")
agent("Do we have PROD-456 available?")
agent("Check inventory for PROD-789")
agent("Can I order PROD-123 right now?")
```

1. **@tool** Without it, this is just regular Python the agent never sees.
2. **The docstring** When someone asks "Is PROD-123 in stock?", the model reads "Check if a product is in stock" and recognises this tool fits.
3. **Args: product_id … (e.g., "PROD-123")** Tells the model which piece of the question to extract, and what it looks like.
4. **inventory = {…}** A dictionary standing in for a database. In production you'd replace it with a real query or an API call to your inventory system; nothing else changes.
5. **return …** A plain sentence the model can use directly in its reply.

Four differently worded questions, and the agent recognises all of them as inventory checks. In traditional chatbot development you would write **regex** patterns or train an **intent classifier** to handle those variations, map "in stock", "available" and "can I order" to the same intent, and extract the product ID from different sentence shapes. Here you skipped all of that. You wrote one function with a clear description, and the language model handles intent recognition and parameter extraction.

{{diagram:1}}

*Four red boxes you no longer build. Intent recognition and parameter extraction move into the model. Your job shrinks to writing a clear function and docstring.*

Try it

##### Regex chatbot vs agent: who understands the question?

**Each question, run through both approaches:**
1. **Is PROD-123 in stock?**
- **Regex chatbot:** Matched. Product PROD-123 is in stock. We have 15 units available.
- **Tool call:** `check_inventory(product_id="PROD-123")`
- **Agent:** “Product PROD-123 is in stock. We have 15 units available.”
2. **Do we have PROD-456 available?**
- **Regex chatbot:** Matched. Product PROD-456 is currently out of stock.
- **Tool call:** `check_inventory(product_id="PROD-456")`
- **Agent:** “Product PROD-456 is currently out of stock.”
3. **Check inventory for PROD-789**
- **Regex chatbot:** “Sorry, I didn't understand that.” No rule for this phrasing. Someone has to add one.
- **Tool call:** `check_inventory(product_id="PROD-789")`
- **Agent:** “Product PROD-789 is in stock. We have 8 units available.”
4. **Can I order PROD-123 right now?**
- **Regex chatbot:** “Sorry, I didn't understand that.” No rule for this phrasing. Someone has to add one.
- **Tool call:** `check_inventory(product_id="PROD-123")`
- **Agent:** “Product PROD-123 is in stock. We have 15 units available.”
5. **Are there any PROD-789 left?**
- **Regex chatbot:** “Sorry, I didn't understand that.” No rule for this phrasing. Someone has to add one.
- **Tool call:** `check_inventory(product_id="PROD-789")`
- **Agent:** “Product PROD-789 is in stock. We have 8 units available.”
6. **I want to buy PROD-456 today, possible?**
- **Regex chatbot:** “Sorry, I didn't understand that.” No rule for this phrasing. Someone has to add one.
- **Tool call:** `check_inventory(product_id="PROD-456")`
- **Agent:** “Product PROD-456 is currently out of stock.”

**If the question has no product ID:** Agent: “Which product ID do you mean? For example, PROD-123.” (product_id is required, so it asks.)

Or type your own e.g. are there any PROD-789 left?

Regex chatbot (matches only "in stock" or "available")

Agent with check_inventory

The agent column runs the real tool logic (15, 0 and 8 units). A small matcher stands in for the model's understanding, so treat it as a demo of the idea.

#### Your turn: build one tool you care about

The best way to make this stick is to build a tool for a problem you actually have. Pick one, write it, give it to an agent, and ask questions in your own words. Rough logic is fine; what matters is seeing your tool fit into the agent loop.

| Idea | A signature to start from | Ask it |
| --- | --- | --- |
| Weather in your city | `get_weather(city: str) -> str` (call a weather API) | "Do I need an umbrella in Pune today?" |
| Validate an email | `is_valid_email(email: str) -> bool` | "Is asha@example a valid address?" |
| Age from birthdate | `age_from_birthdate(birthdate: str) -> int` | "How old is someone born on 1990-08-15?" |
| BMI | `calculate_bmi(height_cm: float, weight_kg: float) -> dict` | "I'm 172 cm and 70 kg, what's my BMI?" |
| Shipping cost | `shipping_cost(weight_kg: float, distance_km: float) -> float` | "Cost to ship 3 kg from Bangalore to Delhi?" |

> **You already know enough for most tools:**
> Plain `@tool` functions cover the majority of what you'll build. As your agents grow, though, you'll hit situations where they aren't enough: several tools sharing an expensive resource, slow APIs, and inputs that need strict validation. You don't need to memorise these now; just know they exist so you recognise them when they show up.

## 2.5 When simple tools aren't enough

Your inventory agent now has five tools: check stock, update stock, get supplier info, track shipments and generate reports. You deploy it. Within an hour your database administrator messages you: "Why is your agent opening 50 database connections per minute?"

You check the logs: every tool opens its own database connection. One user request may trigger three or four tool calls, so three or four connections, and dozens of users at once means the database is drowning. The `@tool` decorator is perfect for simple cases, but as agents grow you need more control. Notebook 3 walks through two such situations with real, countable numbers, using a small local SQLite database.

#### The database connection problem, and class-based tools

First the notebook creates a tiny inventory database and a `connect_to_database()` helper that counts every connection it opens:

```pseudo title="03_advanced_tool_patterns.ipynb: setup"
IMPORT sqlite3
SET DB_PATH = "inventory_demo.db"

// create and seed a small inventory database
open DB_PATH as conn
    remove the old inventory table if it exists
    CREATE the inventory table (id, name, quantity, price)
    add three products: PROD-123 Wireless Mouse, PROD-456 USB-C Hub, PROD-789 Mechanical Keyboard
PRINT "Database ready" and DB_PATH
SET CONNECTIONS_OPENED = 0

DEFINE connect_to_database()
    ADD 1 to CONNECTIONS_OPENED   // count every connection that is opened
    RETURN a new connection to DB_PATH, usable from worker threads
```

> **Imported:**
> - `sqlite3` Python standard library: the built-in database. Here it is a small local file, `inventory_demo.db`.

```python reveal title="03_advanced_tool_patterns.ipynb: setup"
import sqlite3

DB_PATH = "inventory_demo.db"

# Create and seed a small inventory database
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("DROP TABLE IF EXISTS inventory")
    conn.execute("CREATE TABLE inventory (id TEXT PRIMARY KEY, name TEXT, quantity INTEGER, price REAL)")
    conn.executemany(
        "INSERT INTO inventory VALUES (?, ?, ?, ?)",
        [
            ("PROD-123", "Wireless Mouse", 15, 29.99),
            ("PROD-456", "USB-C Hub", 0, 49.99),
            ("PROD-789", "Mechanical Keyboard", 8, 89.99),
        ],
    )
print("Database ready:", DB_PATH)

CONNECTIONS_OPENED = 0

def connect_to_database():
    """Open a new database connection and count it."""
    global CONNECTIONS_OPENED
    CONNECTIONS_OPENED += 1
    # check_same_thread=False: the agent may run tools on worker threads
    return sqlite3.connect(DB_PATH, check_same_thread=False)
```

Now the naive version, where each tool opens a connection, uses it once and closes it:

```pseudo title="03_advanced_tool_patterns.ipynb: one connection per tool call"
IMPORT Agent and tool
DEFINE check_stock(product_id)   // @tool
    SET db = connect_to_database()   // a new connection for this call
    SET row = the quantity for product_id in the inventory table
    close db
    RETURN "product_id: N units", or "product_id not found" if there is no row

DEFINE update_stock(product_id, quantity)   // @tool
    SET db = connect_to_database()   // another new connection
    change the quantity of product_id in the inventory table to quantity
    commit the change
    close db
    RETURN "Updated product_id to quantity units"

SET CONNECTIONS_OPENED = 0   // reset the counter before the request
CREATE agent = Agent(model, tools = [check_stock, update_stock])
ASK agent: "Check stock for PROD-123 and PROD-789, set PROD-456 to 25 units, then confirm PROD-456's new level"
PRINT the number of connections opened for that one request
```

> **Imported:**
> - `Agent` from `strands`: the class that runs the model together with its tools.
> - `tool` from `strands`: the decorator that registers a function as a tool.

```python reveal title="03_advanced_tool_patterns.ipynb: one connection per tool call"
from strands import Agent, tool

@tool
def check_stock(product_id: str) -> str:
    """Check product stock."""
    db = connect_to_database()
    row = db.execute("SELECT quantity FROM inventory WHERE id = ?", (product_id,)).fetchone()
    db.close()
    return f"{product_id}: {row[0]} units" if row else f"{product_id} not found"

@tool
def update_stock(product_id: str, quantity: int) -> str:
    """Update product stock."""
    db = connect_to_database()
    db.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (quantity, product_id))
    db.commit()
    db.close()
    return f"Updated {product_id} to {quantity} units"

CONNECTIONS_OPENED = 0
agent = Agent(model=model, tools=[check_stock, update_stock])
agent("Check stock for PROD-123 and PROD-789, set PROD-456 to 25 units, then confirm PROD-456's new level")

print(f"\n\nConnections opened for one request: {CONNECTIONS_OPENED}")
```

That one request needs four tool calls (two checks, an update, a confirm), so it prints about **4 connections**. Harmless here, painful in production, because opening a connection is expensive:

- **It takes time.** Each new connection needs a handshake, typically 50 to 100 milliseconds over a network, before any query runs.
- **It uses server memory** for every open connection.
- **Databases cap them.** By default MySQL allows 151 simultaneous connections and PostgreSQL 100. Hit the cap and your agent starts failing with "too many connections".

What you want is to connect once when the agent starts and share that connection across all the tools. Separate decorated functions have no place to keep shared state, so the fix is to **group related tools inside a class**:

{{diagram:2}}

*Same tools, different wiring. On the left every call dials the database again. On the right the class holds one open line that every tool method shares.*

```pseudo title="03_advanced_tool_patterns.ipynb: class-based tools"
IMPORT threading

CLASS InventoryTools
    DEFINE __init__(self)
        // one shared connection for every tool on this object
        SET self.db = connect_to_database()   // opened once, here
        SET self.lock = a new lock            // so only one tool call uses the connection at a time

    DEFINE check_stock(self, product_id)   // @tool method
        WITH self.lock:
            SET row = name and quantity for product_id, read from self.db
        RETURN "name (product_id): N units in stock", or "Product product_id not found" if there is no row

    DEFINE update_stock(self, product_id, quantity)   // @tool method
        WITH self.lock:
            change the quantity of product_id to quantity in self.db
            commit the change
        RETURN "Updated product_id to quantity units", or "Product product_id not found" if no row changed

SET CONNECTIONS_OPENED = 0
CREATE inventory = InventoryTools()
CREATE agent = Agent(model, tools = [inventory.check_stock, inventory.update_stock])
ASK agent: "Check stock for PROD-123 and PROD-789, set PROD-456 to 40 units, then confirm PROD-456's new level"
PRINT the number of connections opened for that one request
```

> **Imported:**
> - `threading` Python standard library: provides `Lock`, which makes tool calls take turns on the shared connection.

```python reveal title="03_advanced_tool_patterns.ipynb: class-based tools"
import threading

class InventoryTools:
    def __init__(self):
        # One shared connection for every tool on this object.
        # The agent can run tools in parallel threads, so guard the shared
        # connection with a lock.
        self.db = connect_to_database()
        self.lock = threading.Lock()

    @tool
    def check_stock(self, product_id: str) -> str:
        """Check product stock level.

        Args:
            product_id: The product ID to check
        """
        with self.lock:
            row = self.db.execute("SELECT name, quantity FROM inventory WHERE id = ?", (product_id,)).fetchone()
        return f"{row[0]} ({product_id}): {row[1]} units in stock" if row else f"Product {product_id} not found"

    @tool
    def update_stock(self, product_id: str, quantity: int) -> str:
        """Update product stock quantity.

        Args:
            product_id: The product ID to update
            quantity: New quantity to set
        """
        with self.lock:
            cur = self.db.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (quantity, product_id))
            self.db.commit()
        return f"Updated {product_id} to {quantity} units" if cur.rowcount else f"Product {product_id} not found"

CONNECTIONS_OPENED = 0
inventory = InventoryTools()
agent = Agent(model=model, tools=[inventory.check_stock, inventory.update_stock])
agent("Check stock for PROD-123 and PROD-789, set PROD-456 to 40 units, then confirm PROD-456's new level")

print(f"\n\nConnections opened for one request: {CONNECTIONS_OPENED}")
```

1. **__init__** Runs once when you create `InventoryTools()`. That's where the single connection is opened.
2. **self.lock** Strands may run several tool calls at the same time on different **threads**. The **lock** makes them take turns on the shared connection.
3. **@tool on methods** Tool methods work exactly like tool functions; `self` is hidden from the model.
4. **"… WHERE id = ?", (product_id,)** A **parameterised query**. Never build SQL with f-strings: the values come from the model, so treat them like user input (see **SQL injection**).
5. **tools=[inventory.check_stock, …]** Pass the methods of one object. Now the same request prints **1 connection**.

Try it

##### How many connections does your agent open?

Requests per minute = 30 30

Tool calls per request = 4 4

Function tools (connection per call)

Class tools (one shared connection)

Assumes about 50 ms to open each connection. Connection limits (100 for PostgreSQL, 151 for MySQL by default) count connections open *at the same moment*, so bursts of overlapping requests hit them long before the per-minute total looks scary.

**Default example, 30 requests per minute with 4 tool calls each:**
- **Function tools:** **120** connections opened per minute, about **6.0 s** of every minute spent just opening them.
- **Class tools:** **1** connection per running copy of your app, opened once and reused for all 120 tool calls.

> **Think of it like this:**
> Calling your bank's customer care with four questions. Function tools hang up after each answer and dial again, waiting through the IVR every time. Class tools stay on the same call and ask all four. Same answers, a fraction of the waiting, and the call centre's phone lines stay free for others.

This pattern fits any shared resource: API clients that keep a connection pool, file handles for reading large datasets, connections to a cache like Redis or Memcached, or login tokens that must be refreshed now and then.

#### Slow warehouse checks, and async tools

Two days later your product manager writes: "Users say the agent is too slow. It takes ages to tell them whether an order can ship." To answer "Can we ship 100 units of PROD-123?", the agent checks three warehouses, each with its own API that takes about 2 seconds. Called one after another:

```pseudo title="03_advanced_tool_patterns.ipynb: the slow way"
SET warehouse_a = check_warehouse_inventory("PROD-123", "warehouse_a")   // about 2 seconds
SET warehouse_b = check_warehouse_inventory("PROD-123", "warehouse_b")   // about 2 seconds
SET warehouse_c = check_warehouse_inventory("PROD-123", "warehouse_c")   // about 2 seconds
// total: about 6 seconds, because each call waits for the one before it
```

```python reveal title="03_advanced_tool_patterns.ipynb: the slow way"
warehouse_a = check_warehouse_inventory("PROD-123", "warehouse_a")  # 2 seconds
warehouse_b = check_warehouse_inventory("PROD-123", "warehouse_b")  # 2 seconds
warehouse_c = check_warehouse_inventory("PROD-123", "warehouse_c")  # 2 seconds
# Total: 6 seconds of waiting
```

(The notebook's real tool names the warehouses east, west and central.) Users stare at a spinner and abandon their carts. But look closely: the three checks don't depend on each other. Warehouse B doesn't need A's answer. They could all happen at the same time.

That's what **async** is for. When a function is marked `async`, Python's **event loop** can pause it at each **await** while it waits for slow input/output (like an API response) and switch to other async work on the same thread. Several async functions make progress together, taking turns whenever one is waiting.

{{diagram:3}}

*Waiting in parallel. Total time drops from the sum of the calls to the slowest single call. That only works because the three checks are independent.*

```pseudo title="03_advanced_tool_patterns.ipynb: async tool"
IMPORT asyncio and time

// @tool, marked async so it can pause while it waits
DEFINE async check_warehouse_inventory(product_id, warehouse)
    await asyncio.sleep(2)   // stands in for a 2 second API call
    SET data = the quantities for PROD-123 and PROD-456, per warehouse
    SET quantity = data for warehouse and product_id, or 0 if unknown
    RETURN a dict with warehouse, product_id and quantity

DEFINE async main()
    CREATE agent = Agent(model, tools = [check_warehouse_inventory])
    SET start = time.time()
    await agent.invoke_async("Can we ship 100 units of PROD-123? Check all warehouses: east, west, and central.")
    SET elapsed = time.time() - start
    PRINT the answer, then the total time

await main()   // in Jupyter; in a .py script use asyncio.run(main())
```

> **Imported:**
> - `asyncio` Python standard library: the event loop that runs async code, and `sleep` used here as a stand-in for a slow call.
> - `time` Python standard library: `time.time()` measures how long the request takes.

```python reveal title="03_advanced_tool_patterns.ipynb: async tool"
import asyncio
import time

@tool
async def check_warehouse_inventory(product_id: str, warehouse: str) -> dict:
    """Check inventory at a specific warehouse.

    Args:
        product_id: Product ID to check
        warehouse: Warehouse identifier (e.g., "east", "west", "central")
    """
    await asyncio.sleep(2)  # simulate a slow API call

    data = {
        "east": {"PROD-123": 45, "PROD-456": 12},
        "west": {"PROD-123": 30, "PROD-456": 0},
        "central": {"PROD-123": 60, "PROD-456": 25},
    }
    quantity = data.get(warehouse, {}).get(product_id, 0)
    return {"warehouse": warehouse, "product_id": product_id, "quantity": quantity}

async def main():
    agent = Agent(model=model, tools=[check_warehouse_inventory])
    start = time.time()
    response = await agent.invoke_async(
        "Can we ship 100 units of PROD-123? Check all warehouses: east, west, and central."
    )
    elapsed = time.time() - start
    print("\n\n" + response.message["content"][0]["text"])
    print(f"\nTotal time: {elapsed:.1f}s (three sequential checks alone would take ~6s)")

await main()
```

1. **async def** Marks the tool as pausable.
2. **await asyncio.sleep(2)** Stands in for a 2-second API call. While one call waits here, the others run.
3. **agent.invoke_async(…)** The async way to call an agent. When the model asks for all three checks in one turn, Strands runs them **concurrently**.
4. **await main()** Works in Jupyter, which already has an event loop. In a plain `.py` script use `asyncio.run(main())` instead.
5. **Result** 45 + 30 + 60 = 135 units, so yes, 100 can ship. The tool waiting takes about 2 seconds instead of 6; total time also includes the model's thinking.

In a real tool you'd use an async HTTP client instead of `asyncio.sleep`:

```pseudo title="03_advanced_tool_patterns.ipynb: with a real async HTTP client"
IMPORT httpx

// @tool, async so that waiting on the network does not block other tool calls
DEFINE async check_warehouse_inventory(product_id, warehouse) RETURNS int
    open an async HTTP client as client
        SET response = await client.get the inventory address for warehouse and product_id
    RETURN the quantity field from the JSON response
```

> **Imported:**
> - `httpx` third-party package `httpx`: an HTTP client with async support.

```python reveal title="03_advanced_tool_patterns.ipynb: with a real async HTTP client"
import httpx

@tool
async def check_warehouse_inventory(product_id: str, warehouse: str) -> int:
    """Check inventory at a specific warehouse."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.warehouse-{warehouse}.example.com/inventory/{product_id}")
    return response.json()["quantity"]
```

Run it

##### Race: sequential vs async warehouse checks

Seconds per API call = 2 2

Number of warehouses = 3 3

Sequential

Async

The race plays at 4× speed so you don't wait. The times shown are real-scale.

> **Think of it like this:**
> A waiter with three tables. The slow way: take table 1's order, wait at the kitchen until it's cooked, serve it, then go to table 2. The async way: hand all three orders to the kitchen, and serve each as it's ready. The kitchen still takes the same time per dish; you just stop standing around.

> **Not every tool needs async:**
> If a tool finishes almost instantly (say under 100 ms) or only does calculations with no external calls, async adds complexity and no measurable speed. Start with regular tools; add async when slow I/O actually hurts.

#### Choosing your approach

{{diagram:4}}

*Let real problems guide you, not theoretical ones. The answers aren't exclusive: a class can hold async tool methods if you have both problems.*

Start with the decorator: it's simple and covers most cases. Build, test, deploy, and watch what happens. Connection trouble? Group the tools in a class. Slow external calls? Make them async so they run concurrently.

One more option: if a tool needs strict validation of its inputs (a specific format, or only certain allowed values), Strands lets you write an explicit input schema yourself, called a `TOOL_SPEC`, instead of deriving it from type hints. It's an advanced pattern we won't need in this course. In fact you've already met one: `use_aws` is defined with a `TOOL_SPEC`.
