# Implementing A2A

## 5.10 Implementing A2A

The easiest way to understand the options is as three layers, each built on the one below.

{{diagram:1}}

*Primitives, integrations, platforms. Higher layers implement the protocol for you; lower layers give you more control and more plumbing.*

1. 1 Core protocol layer: the A2A SDK The `a2a-sdk` package is the low-level protocol library, the most direct way to build an A2A client or server. It provides data types such as `Message`, `TextPart`, `AgentSkill` and `AgentCapabilities`, and client utilities such as `A2ACardResolver`, `ClientFactory` and `ClientConfig`. Using only the SDK gives full control, but you wire everything yourself: how your server publishes capabilities, routes requests, creates and updates tasks, and returns responses.
2. 2 Framework integrations Libraries on top of the SDK that implement the protocol for you while keeping your framework's programming model, for example Google ADK and Strands A2A (`strands-agents[a2a]`). Strands provides two key pieces: **`A2AServer`** exposes a Strands agent as an A2A-compliant server, and **`A2AAgent`** lets you use a remote A2A agent as if it were a local Strands agent.
3. 3 Platform-specific implementations Hosted platforms that expose A2A endpoints for agents deployed on them. For example, LangSmith Agent Server is the main way LangChain offers A2A today: the platform handles JSON-RPC messaging and task management, and your agent still takes part in A2A.

| Layer | Example | Gives you |
| --- | --- | --- |
| Protocol primitives | A2A SDK | Every building block, full control, most wiring |
| Framework integration | Strands A2A | An agent becomes a server in a few lines |
| Managed platform | LangSmith Agent Server | Endpoints for agents deployed on that platform |

The lab uses **both** of the first two layers: Strands A2A for the two agent servers (the quickest path from an agent definition to a working A2A server), and the raw A2A SDK for the orchestrator, so you can see the protocol objects directly.

## 5.11 Lab: a travel assistant over A2A

Two independent Strands agents (weather and flights) run as A2A servers. A travel orchestrator discovers them through their **agent cards** and asks each for its part of a trip.

{{diagram:2}}

*Three processes, one protocol. The two agents could be written by different teams in different frameworks; the orchestrator only needs their URLs.*

| File | Role | Description |
| --- | --- | --- |
| `weather_agent_server.py` | A2A server | Weather lookup agent on port 9001 |
| `flights_agent_server.py` | A2A server | Flight search and booking agent on port 9002 |
| `travel_orchestrator.py` | A2A client | Calls both agents and prints a trip summary |

#### The weather agent server

```pseudo title="weather_agent_server.py · imports and settings"
// the weather agent is an A2A server, listening on port 9001
SET MODEL_ID = the BEDROCK_MODEL_ID environment variable, or the default Claude Sonnet 4.6 model
SET REGION = AWS_REGION, else AWS_DEFAULT_REGION, else us-east-1
SET logging level = INFO   // so requests show up in the terminal
```

> **Imported:**
> - `logging` Python standard library: prints what happens during each request.
> - `os` Python standard library: reads the model ID and region from environment variables.
> - `Agent` from `strands`: the core agent class, which wraps an LLM with tools.
> - `tool` from `strands`: the decorator that registers a Python function as a tool the LLM can call.
> - `A2AServer` from `strands.multiagent.a2a`: wraps the Strands agent in an HTTP server that speaks A2A.
> - `AgentSkill` from `a2a.types`, package a2a-sdk: describes one capability in the agent card.
> - `BedrockModel` from `strands.models.bedrock`: the Amazon Bedrock model behind this agent.

```python reveal title="weather_agent_server.py · imports and settings"
"""
Weather Agent — A2A Server on port 9001.

Exposes a weather lookup tool via the Strands A2A protocol.

Run:  python weather_agent_server.py
"""

import logging
import os

# Agent: the core Strands agent class that wraps an LLM with tools
# tool: decorator that registers a Python function as a tool the LLM can call
from strands import Agent, tool

# A2AServer: wraps a Strands Agent into an HTTP server that speaks the A2A protocol
from strands.multiagent.a2a import A2AServer

# AgentSkill: A2A SDK type that describes a capability in the agent card
from a2a.types import AgentSkill

# BedrockModel: the LLM behind this agent (Amazon Bedrock)
from strands.models.bedrock import BedrockModel

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

# Set up logging so we can see what's happening during requests
logging.basicConfig(level=logging.INFO)
```

Note the new import: `A2AServer` from `strands.multiagent.a2a`, and `AgentSkill` from the A2A SDK (`a2a.types`). The model is set explicitly from `BEDROCK_MODEL_ID`, as everywhere in this course.

```pseudo title="weather_agent_server.py · fake data and the tool"
// fake data for the demo, not a real weather API
SET FAKE_WEATHER = a lookup from ten city names to weather text
// @tool registers get_weather so the LLM can call it
DEFINE get_weather(city):   // the docstring tells the LLM when to use it
    SET result = FAKE_WEATHER looked up with city, trimmed and in lower case
    IF result is found THEN
        RETURN "Weather in " + city + ": " + result
    RETURN "No weather data available for '" + city + "'. Available cities: " + the city names joined with commas
```

```python reveal title="weather_agent_server.py · fake data and the tool"
# --- Fake Weather Data ---------------------------------------------------
# In a real app this would call a weather API.
# Here we use a dictionary for demo purposes.

FAKE_WEATHER = {
    "london": "15°C, cloudy with occasional rain",
    "paris": "18°C, sunny with light breeze",
    "tokyo": "22°C, humid and partly cloudy",
    "new york": "12°C, windy and cool",
    "dubai": "38°C, hot and sunny",
    "sydney": "20°C, mild and clear",
    "cancun": "30°C, tropical and sunny",
    "rome": "24°C, warm and sunny",
    "bangkok": "33°C, hot and humid",
    "reykjavik": "5°C, cold and overcast",
}

# --- Weather Tool --------------------------------------------------------
# The @tool decorator registers this function so the LLM can call it.
# The docstring becomes the tool description the LLM sees when deciding
# which tool to use. Args/Returns are parsed for the tool's input schema.

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city.

    Args:
        city: Name of the city to get weather for.

    Returns:
        A string describing the current weather conditions.
    """
    # Normalize input: strip whitespace, lowercase for dictionary lookup
    result = FAKE_WEATHER.get(city.strip().lower())
    if result:
        return f"Weather in {city}: {result}"
    # If city not found, tell the user what cities are available
    return f"No weather data available for '{city}'. Available cities: {', '.join(FAKE_WEATHER.keys())}"
```

```pseudo title="weather_agent_server.py · skills for the agent card"
// skills are published in the agent card, which clients read first
SET WEATHER_SKILLS = a list with one AgentSkill:
    id = "get_weather"
    name = "Get Weather"
    description = "Returns current weather conditions (temperature, sky, wind) for a given city", followed by the ten supported cities
    tags = weather, temperature, forecast, travel   // help clients find the skill
    examples = three sample questions about the weather
```

```python reveal title="weather_agent_server.py · skills for the agent card"
# --- Agent Card Skills ---------------------------------------------------
# Skills are published in the agent card at /.well-known/agent-card.json.
# Any A2A client fetches this card first to discover what the agent can do
# BEFORE sending any messages. Think of it like an API spec for agents.

WEATHER_SKILLS = [
    AgentSkill(
        # Unique identifier for this skill
        id="get_weather",
        # Human-readable name shown in the agent card
        name="Get Weather",
        # Detailed description — helps clients understand what this skill does
        description=(
            "Returns current weather conditions (temperature, sky, wind) "
            "for a given city. Supports: London, Paris, Tokyo, New York, "
            "Dubai, Sydney, Cancun, Rome, Bangkok, Reykjavik."
        ),
        # Tags for categorization and discovery
        tags=["weather", "temperature", "forecast", "travel"],
        # Example prompts — hints to clients on how to use this skill
        examples=[
            "What is the weather in London?",
            "How hot is it in Dubai right now?",
            "Tell me the weather conditions in Tokyo",
        ],
    ),
]
```

`AgentSkill` describes each capability, or **skill**, with an `id`, `name`, `description`, `tags` and example prompts. Passed to the server as `skills=WEATHER_SKILLS`, they appear in the agent card, which clients fetch *first* to understand what the agent can do. Think of it as an API spec for agents.

```pseudo title="weather_agent_server.py · the Strands agent"
// the agent combines an LLM, a system prompt and tools
CREATE weather_agent = Agent(
    model = BedrockModel(MODEL_ID, REGION)   // the LLM, chosen by BEDROCK_MODEL_ID
    name = "Weather Agent"   // used in the agent card
    description = "Provides current weather information for cities around the world."
    system_prompt = "You are a helpful weather assistant. Use the get_weather tool to look up weather conditions for any city the user asks about. Be concise and friendly."
    tools = [get_weather]   // functions the LLM may call
    callback_handler = None   // answers go back over HTTP, so nothing is printed
)
```

```python reveal title="weather_agent_server.py · the Strands agent"
# --- Strands Agent -------------------------------------------------------
# This is the actual AI agent. It combines:
#   - An LLM (Amazon Bedrock, chosen by BEDROCK_MODEL_ID)
#   - A system prompt (instructions for the LLM)
#   - Tools (functions the LLM can call)
#
# When a message comes in, the agent sends it to the LLM. The LLM reads
# the system prompt, sees the available tools, and decides whether to call
# get_weather. If it does, the tool runs, and the LLM formats the final answer.

weather_agent = Agent(
    # The LLM that powers this agent
    model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
    # Name and description — used in the A2A agent card
    name="Weather Agent",
    description="Provides current weather information for cities around the world.",
    # System prompt — instructions the LLM follows for every request
    system_prompt=(
        "You are a helpful weather assistant. Use the get_weather tool to look up "
        "weather conditions for any city the user asks about. Be concise and friendly."
    ),
    # Register the get_weather tool so the LLM can call it
    tools=[get_weather],
    # Disable streaming callback on the server side (responses are collected, not printed)
    callback_handler=None,
)
```

An ordinary Strands agent. Two details matter for A2A: `name` and `description` become the agent card's name and description (Strands refuses to build a card if either is empty), and `callback_handler=None` stops the server printing every response, since answers go back over HTTP instead.

```pseudo title="weather_agent_server.py · serve it over A2A"
// only runs when this file is run directly
IF this file is run directly THEN
    CREATE server = A2AServer(agent = weather_agent, host = "127.0.0.1", port = 9001, skills = WEATHER_SKILLS, version = "1.0.0", enable_a2a_compliant_streaming = True)   // 127.0.0.1 means this machine only
    PRINT "Weather Agent A2A server starting on http://127.0.0.1:9001"
    RUN server.serve()   // serves the agent card and accepts A2A messages until Ctrl+C
```

```python reveal title="weather_agent_server.py · serve it over A2A"
# --- A2A Server ----------------------------------------------------------
# Only runs when you execute this file directly (python weather_agent_server.py).
# Importing this file from another module won't start the server.

if __name__ == "__main__":
    # A2AServer wraps the Strands Agent into an HTTP server that:
    #   1. Serves an agent card at GET /.well-known/agent-card.json
    #   2. Accepts A2A messages at POST / (JSON-RPC: message/send, message/sendStream)
    #   3. Routes messages through the Strands Agent (LLM + tools)
    #   4. Returns responses as A2A task objects with artifacts
    server = A2AServer(
        # The Strands Agent that handles all incoming messages
        agent=weather_agent,
        # Bind to localhost only (use "0.0.0.0" to expose to network)
        host="127.0.0.1",
        # HTTP port to listen on
        port=9001,
        # Skills published in the agent card for client discovery
        skills=WEATHER_SKILLS,
        # Version string in the agent card
        version="1.0.0",
        # Use A2A-spec-compliant SSE streaming with artifact updates
        # (vs legacy status-only streaming). The agent card will advertise
        # {"capabilities": {"streaming": true}} so clients know SSE is supported.
        enable_a2a_compliant_streaming=True,
    )
    print("Weather Agent A2A server starting on http://127.0.0.1:9001")
    # Start the uvicorn HTTP server. This is a blocking call —
    # the process stays alive serving requests until you Ctrl+C.
    server.serve()
```

| Argument | What it does |
| --- | --- |
| `agent=weather_agent` | The Strands agent that handles every incoming message |
| `host="127.0.0.1"` | Listen on this machine only (`"0.0.0.0"` would expose it to the network) |
| `port=9001` | The HTTP port |
| `skills=WEATHER_SKILLS` | Published in the agent card for discovery |
| `version="1.0.0"` | The agent's version, shown in the card |
| `enable_a2a_compliant_streaming=True` | When a client asks for streaming, reply with spec-compliant SSE events including artifact updates (instead of older status-only streaming). Strands' `A2AServer` always advertises `"streaming": true` in the card; this flag only chooses the event format. |

> **Method names in the comments:**
> The comment above mentions `message/sendStream`, and `flights_agent_server.py` has the same comment. In the A2A SDK version this lab installs (0.3), the streaming method on the wire is called `message/stream`; the non-streaming one is `message/send`. The client picks the right one for you, so nothing in the code needs changing.

`server.serve()` starts a web server (**uvicorn**) and blocks until you press Ctrl+C. Your agent is now a stand-alone HTTP microservice that speaks A2A. Its card, at `http://127.0.0.1:9001/.well-known/agent-card.json`, looks like this:

```pseudo title="GET /.well-known/agent-card.json"
// the JSON document the weather server returns for this URL (abridged)
SET card = a JSON document with:
    name = "Weather Agent"
    description = "Provides current weather information for cities around the world."
    version = "1.0.0", protocolVersion = "0.3.0", preferredTransport = JSONRPC
    capabilities: streaming = true   // so clients use SSE streaming
    skills = one skill, get_weather, with its description, tags and examples
    defaultInputModes = text, defaultOutputModes = text
    url = "http://127.0.0.1:9001/"   // where clients send messages
```

```json reveal title="GET /.well-known/agent-card.jsonabridged"
{
  "name": "Weather Agent",
  "description": "Provides current weather information for cities around the world.",
  "version": "1.0.0",
  "protocolVersion": "0.3.0",
  "preferredTransport": "JSONRPC",
  "capabilities": { "streaming": true },
  "skills": [
    {
      "id": "get_weather",
      "name": "Get Weather",
      "description": "Returns current weather conditions...",
      "tags": ["weather", "temperature", "forecast", "travel"],
      "examples": ["What is the weather in London?", "..."]
    }
  ],
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "url": "http://127.0.0.1:9001/"
}
```

> **agent= vs agent_factory=:**
> In recent Strands versions, passing a single `agent=` is **deprecated** (you may see a `DeprecationWarning`) in favour of `A2AServer(agent_factory=...)`, a function that builds a fresh agent per conversation, for servers that many callers use at once. For this one-user demo, `agent=` still works; every caller simply shares the same agent.

#### The flights agent server

Same pattern, with two tools and two skills, on port 9002.

```pseudo title="flights_agent_server.py · fake data"
// fake data, keyed by an (origin, destination) pair
SET FAKE_FLIGHTS = a lookup from six routes to their lists of flights
    each flight has an airline, a flight number, depart, arrive and price
```

```python reveal title="flights_agent_server.py · fake data"
# --- Fake Flight Data ----------------------------------------------------
# In a real app this would query a flights API or database.
# Here we use a dictionary keyed by (origin, destination) tuples.

FAKE_FLIGHTS = {
    ("london", "paris"): [
        {"airline": "AirEurope", "flight": "AE101", "depart": "08:00", "arrive": "10:30", "price": "$120"},
        {"airline": "SkyWings", "flight": "SW202", "depart": "14:00", "arrive": "16:30", "price": "$95"},
    ],
    ("new york", "london"): [
        {"airline": "TransAtlantic", "flight": "TA501", "depart": "22:00", "arrive": "10:00+1", "price": "$450"},
        {"airline": "AirEurope", "flight": "AE303", "depart": "18:00", "arrive": "06:00+1", "price": "$380"},
    ],
    ("tokyo", "sydney"): [
        {"airline": "PacificAir", "flight": "PA701", "depart": "09:00", "arrive": "20:00", "price": "$520"},
    ],
    ("paris", "rome"): [
        {"airline": "AirEurope", "flight": "AE150", "depart": "07:30", "arrive": "09:30", "price": "$85"},
        {"airline": "MedFly", "flight": "MF44", "depart": "12:00", "arrive": "14:00", "price": "$70"},
    ],
    ("dubai", "bangkok"): [
        {"airline": "GulfAir", "flight": "GA880", "depart": "02:00", "arrive": "12:00", "price": "$340"},
    ],
    ("new york", "cancun"): [
        {"airline": "SunJet", "flight": "SJ610", "depart": "06:00", "arrive": "10:00", "price": "$250"},
        {"airline": "SkyWings", "flight": "SW415", "depart": "11:00", "arrive": "15:00", "price": "$210"},
    ],
}
```

```pseudo title="flights_agent_server.py · tools"
// each @tool function is a tool the LLM can call
DEFINE search_flights(origin, destination):   // the docstring tells the LLM when to use it
    SET key = (origin, destination), trimmed and in lower case
    SET flights = FAKE_FLIGHTS looked up with key
    IF no flights are found THEN
        RETURN "No flights found from origin to destination", followed by the available routes
    SET lines = a heading "Flights from origin to destination:"
    FOR EACH flight in flights ADD one line with airline, flight number, depart, arrive and price
    RETURN the lines joined with new lines

DEFINE book_flight(flight_number, passenger_name):
    FOR EACH flight on every route
        IF its flight number matches flight_number, ignoring case and surrounding spaces THEN
            RETURN "Booking confirmed!" with the passenger name, airline, flight, times, price and a confirmation number
    RETURN "Flight " + flight_number + " not found. Please search for available flights first."
```

```python reveal title="flights_agent_server.py · tools"
# --- Flight Tools --------------------------------------------------------
# Each @tool-decorated function becomes a tool the LLM can call.
# The docstring is what the LLM sees when deciding which tool to use.
# Args/Returns are parsed to build the tool's input schema automatically.

@tool
def search_flights(origin: str, destination: str) -> str:
    """Search for available flights between two cities.

    Args:
        origin: Departure city name.
        destination: Arrival city name.

    Returns:
        A formatted list of available flights or a message if none found.
    """
    # Normalize both cities to lowercase for dictionary lookup
    key = (origin.strip().lower(), destination.strip().lower())
    flights = FAKE_FLIGHTS.get(key)

    # If no flights found, show the user what routes are available
    if not flights:
        available = [f"{o.title()} -> {d.title()}" for o, d in FAKE_FLIGHTS.keys()]
        return (
            f"No flights found from {origin} to {destination}. "
            f"Available routes: {', '.join(available)}"
        )

    # Format each flight as a readable line
    lines = [f"Flights from {origin.title()} to {destination.title()}:"]
    for f in flights:
        lines.append(
            f"  {f['airline']} {f['flight']}: depart {f['depart']}, "
            f"arrive {f['arrive']}, price {f['price']}"
        )
    return "\n".join(lines)

@tool
def book_flight(flight_number: str, passenger_name: str) -> str:
    """Book a specific flight for a passenger.

    Args:
        flight_number: The flight number to book (e.g. AE101).
        passenger_name: Name of the passenger.

    Returns:
        Booking confirmation or error message.
    """
    # Search all routes for the matching flight number
    for flights in FAKE_FLIGHTS.values():
        for f in flights:
            if f["flight"].upper() == flight_number.strip().upper():
                # Generate a fake confirmation number from a hash
                return (
                    f"Booking confirmed! {passenger_name} is booked on "
                    f"{f['airline']} flight {f['flight']} "
                    f"(depart {f['depart']}, arrive {f['arrive']}). "
                    f"Total: {f['price']}. Confirmation #: TRV-{hash(flight_number + passenger_name) % 100000:05d}"
                )
    return f"Flight {flight_number} not found. Please search for available flights first."
```

Routes are keyed by `(origin, destination)` in lower case, so "New York" and "new york" both work. An unknown route returns the list of available routes, a friendly error the LLM can relay. `book_flight` searches every route for the flight number and returns a confirmation with a made-up number (built from a `hash`, so it changes between Python runs).

#### **See the rest of `flights_agent_server.py`** (skills, agent and server)

```pseudo title="flights_agent_server.py · skills, agent, server"
// skills for the agent card: searching and booking
SET FLIGHTS_SKILLS = a list with two AgentSkill entries:
    search_flights, named "Search Flights", with tags and examples
    book_flight, named "Book Flight", with tags and examples
CREATE flights_agent = Agent(
    model = BedrockModel(MODEL_ID, REGION)   // the LLM behind the agent
    name = "Flights Agent"   // used in the agent card
    description = "Searches for flights between cities and handles bookings."
    system_prompt = the flight booking instructions: use search_flights and book_flight, be concise
    tools = [search_flights, book_flight]
    callback_handler = None   // answers go back over HTTP, so nothing is printed
)
IF this file is run directly THEN
    CREATE server = A2AServer(agent = flights_agent, host = "127.0.0.1", port = 9002, skills = FLIGHTS_SKILLS, version = "1.0.0", enable_a2a_compliant_streaming = True)
    PRINT "Flights Agent A2A server starting on http://127.0.0.1:9002"
    RUN server.serve()   // blocks until Ctrl+C
```

```python reveal title="flights_agent_server.py · skills, agent, server"
# --- Agent Card Skills ---------------------------------------------------
# Skills are published in the agent card at /.well-known/agent-card.json.
# Any A2A client fetches this card first to discover what the agent can do
# BEFORE sending any messages. Think of it like an API spec for agents.

FLIGHTS_SKILLS = [
    AgentSkill(
        # Unique identifier for this skill
        id="search_flights",
        # Human-readable name shown in the agent card
        name="Search Flights",
        # Detailed description — helps clients understand what this skill does
        description=(
            "Searches for available flights between two cities. "
            "Returns airline, flight number, departure/arrival times, and price. "
            "Available routes: London→Paris, New York→London, Tokyo→Sydney, "
            "Paris→Rome, Dubai→Bangkok, New York→Cancun."
        ),
        # Tags for categorization and discovery
        tags=["flights", "search", "travel", "airlines", "booking"],
        # Example prompts — hints to clients on how to use this skill
        examples=[
            "Find flights from New York to London",
            "Search for flights from Paris to Rome",
            "What flights go from Dubai to Bangkok?",
        ],
    ),
    AgentSkill(
        id="book_flight",
        name="Book Flight",
        description=(
            "Books a specific flight for a passenger given a flight number "
            "and passenger name. Returns a booking confirmation with a "
            "confirmation number."
        ),
        tags=["booking", "reservation", "flights", "travel"],
        examples=[
            "Book flight AE303 for John Smith",
            "Reserve flight TA501 for Jane Doe",
        ],
    ),
]

# --- Strands Agent -------------------------------------------------------
# This is the actual AI agent. It combines:
#   - An LLM (Amazon Bedrock, chosen by BEDROCK_MODEL_ID)
#   - A system prompt (instructions for the LLM)
#   - Tools (functions the LLM can call)
#
# When a message comes in, the agent sends it to the LLM. The LLM reads
# the system prompt, sees the available tools, and decides whether to call
# search_flights or book_flight. The tool runs, and the LLM formats the answer.

flights_agent = Agent(
    # The LLM that powers this agent
    model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
    # Name and description — used in the A2A agent card
    name="Flights Agent",
    description="Searches for flights between cities and handles bookings.",
    # System prompt — instructions the LLM follows for every request
    system_prompt=(
        "You are a helpful flight booking assistant. Use search_flights to find "
        "available flights between cities, and book_flight to make reservations. "
        "Be concise and provide clear flight options."
    ),
    # Register both tools so the LLM can call them
    tools=[search_flights, book_flight],
    # Disable streaming callback on the server side (responses are collected, not printed)
    callback_handler=None,
)

# --- A2A Server ----------------------------------------------------------
# Only runs when you execute this file directly (python flights_agent_server.py).

if __name__ == "__main__":
    # A2AServer wraps the Strands Agent into an HTTP server that:
    #   1. Serves an agent card at GET /.well-known/agent-card.json
    #   2. Accepts A2A messages at POST / (JSON-RPC: message/send, message/sendStream)
    #   3. Routes messages through the Strands Agent (LLM + tools)
    #   4. Returns responses as A2A task objects with artifacts
    server = A2AServer(
        # The Strands Agent that handles all incoming messages
        agent=flights_agent,
        # Bind to localhost only (use "0.0.0.0" to expose to network)
        host="127.0.0.1",
        # HTTP port to listen on
        port=9002,
        # Skills published in the agent card for client discovery
        skills=FLIGHTS_SKILLS,
        # Version string in the agent card
        version="1.0.0",
        # Use A2A-spec-compliant SSE streaming with artifact updates
        enable_a2a_compliant_streaming=True,
    )
    print("Flights Agent A2A server starting on http://127.0.0.1:9002")
    # Start the uvicorn HTTP server — blocking call, runs until Ctrl+C
    server.serve()
```

#### The travel orchestrator (A2A client)

This program has **no LLM**. It just sends A2A messages to the two servers and prints what comes back, so you can see the protocol objects directly.

```pseudo title="travel_orchestrator.py · imports and settings"
// the A2A client: no LLM, only messages sent to the two servers
IMPORT the standard modules: sys, asyncio, logging, and uuid4
IMPORT httpx, the async HTTP client
IMPORT A2ACardResolver, ClientConfig, ClientFactory, Message, Part, Role and TextPart from the A2A SDK
SET logging level = INFO
SET logger = a logger for this module
SET WEATHER_URL = "http://127.0.0.1:9001"
SET FLIGHTS_URL = "http://127.0.0.1:9002"
SET TIMEOUT = 300 seconds   // agents may take a while, because they call an LLM
```

> **Imported:**
> - `sys` Python standard library: reads the command-line arguments in `sys.argv`.
> - `asyncio` Python standard library: runs the async `main` function.
> - `logging` Python standard library: shows the A2A protocol activity as INFO lines.
> - `uuid4` from `uuid`, Python standard library: makes a unique ID for each message.
> - `httpx` the httpx package: the async HTTP client used to talk to the servers.
> - `A2ACardResolver` from `a2a.client`, package a2a-sdk: fetches an agent card from `/.well-known/agent-card.json`.
> - `ClientConfig` from `a2a.client`, package a2a-sdk: sets the client options, such as streaming and the HTTP client.
> - `ClientFactory` from `a2a.client`, package a2a-sdk: builds an A2A client from an agent card.
> - `Message` from `a2a.types`, package a2a-sdk: the envelope for one message.
> - `Part` from `a2a.types`, package a2a-sdk: wraps the content of a message.
> - `Role` from `a2a.types`, package a2a-sdk: says who sent the message (user or agent).
> - `TextPart` from `a2a.types`, package a2a-sdk: holds the text itself.

```python reveal title="travel_orchestrator.py · imports and settings"
"""
Travel Orchestrator — A2A client that talks to Weather + Flights agents.

This is the A2A CLIENT side. It connects to two remote A2A agent servers,
sends them messages using the A2A protocol, and prints the results.

No LLM here — just direct A2A request/response.

Prerequisites:
    1. Start weather agent:  python weather_agent_server.py
    2. Start flights agent:  python flights_agent_server.py
    3. Run this:             python travel_orchestrator.py

Usage:
    python travel_orchestrator.py
    python travel_orchestrator.py "London" "New York" "London"
"""

import sys
import asyncio
import logging
from uuid import uuid4

# httpx: async HTTP client used to make requests to the A2A servers
import httpx

# A2ACardResolver: fetches the agent card from /.well-known/agent-card.json
# ClientConfig: configures the A2A client (streaming vs sync, timeout, etc.)
# ClientFactory: creates an A2A client from an agent card
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory

# A2A message types used to construct the request
# Message: the envelope for a user or agent message
# Part/TextPart: wraps the actual text content
# Role: identifies the sender (user or agent)
from a2a.types import Message, Part, Role, TextPart

# Set up logging so we can see A2A protocol activity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs of the two A2A agent servers
WEATHER_URL = "http://127.0.0.1:9001"
FLIGHTS_URL = "http://127.0.0.1:9002"

# Timeout for HTTP requests (5 minutes — agents may take time with LLM calls)
TIMEOUT = 300
```

```pseudo title="travel_orchestrator.py · step 1 build a message, step 3 extract text"
// make_message: the A2A equivalent of typing a question in a chat box
DEFINE make_message(text):
    RETURN a Message with:
        kind = "message"
        role = user   // the question comes from the user
        parts = one text part holding text
        message_id = a new unique ID

// extract_text: the answer lives in the task's artifacts
DEFINE extract_text(result):
    IF result has artifacts THEN
        SET texts = an empty list
        FOR EACH artifact in result.artifacts
            FOR EACH part in artifact.parts
                IF the part has text inside its root THEN ADD that text to texts
                ELSE IF the part has text THEN ADD that text to texts
        IF texts is not empty THEN
            RETURN all the texts joined together
    RETURN the raw result as a string   // fallback
```

```python reveal title="travel_orchestrator.py · step 1 build a message, step 3 extract text"
# --- Helper: Build an A2A Message ----------------------------------------
# Creates a standard A2A Message object that the server expects.
# This is the equivalent of a user typing a question in a chat.

def make_message(text: str) -> Message:
    return Message(
        kind="message",          # Always "message" for chat messages
        role=Role.user,          # We're the user sending a question
        parts=[Part(TextPart(    # Wrap the text in a TextPart inside a Part
            kind="text",
            text=text,
        ))],
        message_id=uuid4().hex,  # Unique ID for this message
    )

# --- Helper: Extract Text from A2A Response ------------------------------
# A2A servers return a "task" object. The actual answer text lives inside
# task.artifacts[].parts[].text. This function digs it out.

def extract_text(result) -> str:
    """Pull text out of an A2A task response (from artifacts)."""
    if hasattr(result, "artifacts") and result.artifacts:
        texts = []
        for artifact in result.artifacts:
            for part in artifact.parts:
                # The a2a SDK wraps parts in a discriminated union (Part.root)
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    texts.append(part.root.text)
                elif hasattr(part, "text"):
                    texts.append(part.text)
        if texts:
            return "".join(texts)
    # Fallback: return the raw string representation
    return str(result)
```

1. 1 `make_message`: build an A2A message A `Message` with `role=Role.user`, one text part (`Part(TextPart(...))`), and a unique `message_id`. It's the A2A equivalent of a user typing in a chat box.
2. 3 `extract_text`: dig the answer out A2A servers return a **task**; the answer lives in `task.artifacts[].parts[]`. The SDK wraps each part in a container that can hold any kind of part (text, file or data) and keeps the real part in `part.root`, so the code checks both shapes and falls back to the raw text if needed.

```pseudo title="travel_orchestrator.py · step 2 discover and send"
DEFINE send_a2a_message(base_url, text):   // streaming or sync, chosen from the agent card
    CREATE hc = an httpx.AsyncClient with timeout TIMEOUT   // closed when the block ends
    CREATE resolver = A2ACardResolver(hc, base_url)
    CALL resolver.get_agent_card() and WAIT   // fetches /.well-known/agent-card.json
    SET use_streaming = true if the card says streaming is true, else false
    SET mode = "streaming" or "sync", to match
    log the agent name and the mode
    CREATE client = ClientFactory(ClientConfig(hc, streaming = use_streaming)).create(card)
    SET msg = make_message(text)
    SET final_text = empty
    FOR EACH event in client.send_message(msg)
        IF the event has artifacts THEN
            SET final_text = extract_text(event)
        ELSE IF the event is a (task, update) pair with artifacts THEN
            SET final_text = extract_text(task)
        ELSE IF the event is an intermediate Message THEN
            skip it, and wait for the final artifacts   // they hold the complete answer
    RETURN final_text, or "No response received." if it is empty
```

```python reveal title="travel_orchestrator.py · step 2 discover and send"
# --- Core: Send a Message to an A2A Agent --------------------------------
# This is the main A2A client logic. It:
#   1. Fetches the agent card to discover capabilities
#   2. Auto-selects streaming or sync mode based on the card
#   3. Sends the message using the A2A protocol
#   4. Extracts and returns the text response

async def send_a2a_message(base_url: str, text: str) -> str:
    """Send a message to an A2A agent, auto-selecting streaming or sync based on the agent card."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as hc:

        # Step 1: Fetch the agent card from /.well-known/agent-card.json
        # This tells us the agent's name, skills, and whether it supports streaming
        resolver = A2ACardResolver(httpx_client=hc, base_url=base_url)
        card = await resolver.get_agent_card()

        # Step 2: Check the agent card capabilities to decide the mode
        # If the server advertises {"capabilities": {"streaming": true}},
        # we use SSE streaming; otherwise we use sync (single response)
        use_streaming = bool(card.capabilities and card.capabilities.streaming)
        mode = "streaming" if use_streaming else "sync"
        logger.info(f"Connected to: {card.name} — mode: {mode}")

        # Step 3: Create an A2A client configured for this agent
        # ClientConfig sets streaming mode; ClientFactory builds the client from the card
        config = ClientConfig(httpx_client=hc, streaming=use_streaming)
        client = ClientFactory(config).create(card)

        # Step 4: Send the message and process response events
        # In sync mode: yields one task with artifacts (the final answer)
        # In streaming mode: yields intermediate Messages + final task with artifacts
        msg = make_message(text)
        final_text = ""

        async for event in client.send_message(msg):
            # Task with artifacts — this is the final complete response
            if hasattr(event, "artifacts") and event.artifacts:
                final_text = extract_text(event)

            # (Task, UpdateEvent) tuple — check for artifacts on the task
            elif isinstance(event, tuple) and len(event) == 2:
                task, _ = event
                if hasattr(task, "artifacts") and task.artifacts:
                    final_text = extract_text(task)

            # Intermediate streaming Message — we skip these and wait for
            # the final artifacts which contain the complete answer
            elif isinstance(event, Message):
                pass

        return final_text if final_text else "No response received."
```

1. a Fetch the agent card `A2ACardResolver(...).get_agent_card()` downloads `/.well-known/agent-card.json`: name, skills, capabilities.
2. b Pick the mode from the card If the card says `streaming: true`, use streaming (SSE); otherwise a single synchronous response. That's capability negotiation in two lines.
3. c Create a client for *that* agent `ClientFactory(ClientConfig(...)).create(card)` builds a client configured from the card: URL, binding, streaming.
4. d Send and read the events `client.send_message(msg)` sends the JSON-RPC request and yields events. Both cards in this lab say `streaming: true`, so it is always `message/stream` here; against an agent without streaming, the same code would send `message/send`. A task with artifacts, or a `(task, update)` pair, carries the answer; intermediate streaming messages are skipped until the final artifacts arrive.

```pseudo title="travel_orchestrator.py · step 4 the trip summary"
DEFINE main(city, origin, destination):
    PRINT a banner: Travel Orchestrator (A2A)
    // 1. ask the weather agent for conditions at the destination
    PRINT the question sent to the Weather Agent
    SET weather = send_a2a_message(WEATHER_URL, "What is the weather in city?") and WAIT
    PRINT the weather response
    // 2. ask the flights agent for flights on the route
    PRINT the question sent to the Flights Agent
    SET flights = send_a2a_message(FLIGHTS_URL, "Search flights from origin to destination") and WAIT
    PRINT the flights response
    // 3. print a combined trip summary
    PRINT the destination, the weather and the flights

IF this file is run directly THEN
    IF sys.argv has 4 items (the script plus 3 arguments) THEN
        RUN asyncio.run(main(city, origin, destination)) with the arguments you gave
    ELSE
        RUN asyncio.run(main("London", "New York", "London"))   // the default demo
```

```python reveal title="travel_orchestrator.py · step 4 the trip summary"
# --- Main: Orchestrate Calls to Both Agents ------------------------------
# Sends one request to the Weather Agent and one to the Flights Agent,
# then prints a combined trip summary.

async def main(city: str, origin: str, destination: str):
    print("=" * 60)
    print("  Travel Orchestrator (A2A)")
    print("=" * 60)

    # 1. Ask Weather Agent for current conditions at the destination
    print(f"\n>>> Asking Weather Agent: weather in {city}")
    weather = await send_a2a_message(WEATHER_URL, f"What is the weather in {city}?")
    print(f"<<< Weather Agent response:\n{weather}")

    # 2. Ask Flights Agent for available flights on the route
    print(f"\n>>> Asking Flights Agent: flights from {origin} to {destination}")
    flights = await send_a2a_message(FLIGHTS_URL, f"Search flights from {origin} to {destination}")
    print(f"<<< Flights Agent response:\n{flights}")

    # 3. Print a combined trip summary
    print("\n" + "=" * 60)
    print("  Trip Summary")
    print("=" * 60)
    print(f"\nDestination: {city}")
    print(f"Weather: {weather.strip()}")
    print(f"\nFlights ({origin} → {destination}):")
    print(flights.strip())

# --- Entry Point ---------------------------------------------------------
# Supports two modes:
#   - Default: demo with London / New York → London
#   - Custom:  pass city, origin, destination as arguments

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # python travel_orchestrator.py <city> <origin> <destination>
        asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        # Default demo
        asyncio.run(main("London", "New York", "London"))
```

#### What happens on the wire

{{diagram:3}}

*Card first, then message, then task. The orchestrator never sees the tool call; the weather agent stays opaque.*

1. 1 The client fetches the agent card to discover what the agent can do
2. 2 It sends a JSON-RPC message request (`message/stream` here, because the card says streaming) with the user's question
3. 3 The server's Strands agent processes it, calls its tools, and streams back events that end in a task with artifacts holding the final text

#### Run it in three terminals

> **Every terminal needs the same setup:**
> Each new terminal starts fresh. In all three, `cd` into `section-05-mcp-and-a2a/a2a-travel-agents`, activate the course's virtual environment, and make sure your AWS credentials and `AWS_REGION` are set there too.

```pseudo title="terminal"
RUN pip install -r requirements.txt
// terminal 1
RUN python weather_agent_server.py
// terminal 2
RUN python flights_agent_server.py
// terminal 3: the default demo, New York to London
RUN python travel_orchestrator.py
// or give the city, origin and destination
RUN python travel_orchestrator.py "Rome" "Paris" "Rome"
```

```bash reveal title="terminal"
pip install -r requirements.txt

# Terminal 1
python weather_agent_server.py

# Terminal 2
python flights_agent_server.py

# Terminal 3 — default demo (New York → London)
python travel_orchestrator.py

# Or specify city, origin, destination
python travel_orchestrator.py "Rome" "Paris" "Rome"
```

You need AWS credentials with Bedrock access; each agent uses `BEDROCK_MODEL_ID` (default Claude Sonnet 4.6). Start terminals 1 and 2 first and wait until each shows `Uvicorn running on http://127.0.0.1:9001` (or `:9002`). The results print in terminal 3; the grey `INFO` lines are the protocol at work: fetch the card, decide the mode, POST the message.

```text title="terminal 3 outputillustrative; the agents word their answers freely"
============================================================
  Travel Orchestrator (A2A)
============================================================

>>> Asking Weather Agent: weather in London
INFO:httpx:HTTP Request: GET http://127.0.0.1:9001/.well-known/agent-card.json "HTTP/1.1 200 OK"
INFO:a2a.client.card_resolver:Successfully fetched agent card data from http://127.0.0.1:9001/.well-known/agent-card.json: {…}
INFO:__main__:Connected to: Weather Agent — mode: streaming
INFO:httpx:HTTP Request: POST http://127.0.0.1:9001/ "HTTP/1.1 200 OK"
<<< Weather Agent response:
The weather in London is currently 15°C, cloudy with occasional rain. You may want an umbrella!

>>> Asking Flights Agent: flights from New York to London
INFO:httpx:HTTP Request: GET http://127.0.0.1:9002/.well-known/agent-card.json "HTTP/1.1 200 OK"
INFO:a2a.client.card_resolver:Successfully fetched agent card data from …
INFO:__main__:Connected to: Flights Agent — mode: streaming
INFO:httpx:HTTP Request: POST http://127.0.0.1:9002/ "HTTP/1.1 200 OK"
<<< Flights Agent response:
Here are the available flights from New York to London:
1. TransAtlantic TA501: departs 22:00, arrives 10:00 (+1 day), $450
2. AirEurope AE303: departs 18:00, arrives 06:00 (+1 day), $380

============================================================
  Trip Summary
============================================================

Destination: London
Weather: The weather in London is currently 15°C, cloudy with occasional rain. …

Flights (New York → London):
Here are the available flights from New York to London: …
```

| Available data |  |
| --- | --- |
| Weather cities | London, Paris, Tokyo, New York, Dubai, Sydney, Cancun, Rome, Bangkok, Reykjavik |
| Flight routes | London→Paris, New York→London, Tokyo→Sydney, Paris→Rome, Dubai→Bangkok, New York→Cancun |

Try it

##### Run the orchestrator

Destination city (weather)

Route (flights)

on Terminal 2 isn't running (flights agent down)

**Default demo: Destination London, route New York → London, flights agent running.**

**Terminal 3**

```bash
python travel_orchestrator.py "London" "New York" "London"
```

Three arguments: the city for the weather, then the flight origin and destination.

**→ Weather agent :9001 · `GET /.well-known/agent-card.json`**

Step 1: discover the agent before talking to it.

**← Agent card**

```text
{ "name": "Weather Agent", "capabilities": { "streaming": true },
  "skills": [ { "id": "get_weather", … } ] }
```

`streaming: true`, so the orchestrator logs `mode: streaming` and will use `message/stream`.

**→ `POST /` · JSON-RPC `message/stream`**

```text
{ "role": "user", "parts": [ { "kind": "text",
  "text": "What is the weather in London?" } ] }
```

**← Task completed · artifact**

```text
The weather in London is currently 15°C, cloudy with occasional rain.
```

Inside, the agent's LLM called `get_weather("London")` and got `Weather in London: 15°C, cloudy with occasional rain`. The orchestrator never sees that call. (The real wording varies; the facts come from the tool.)

**→ Flights agent :9002 · `GET /.well-known/agent-card.json`**

**← Agent card**

```text
{ "name": "Flights Agent", "capabilities": { "streaming": true },
  "skills": [ { "id": "search_flights", … }, { "id": "book_flight", … } ] }
```

**→ `POST /` · JSON-RPC `message/stream`**

```text
{ "role": "user", "parts": [ { "kind": "text",
  "text": "Search flights from New York to London" } ] }
```

**← Task completed · artifact**

```text
Here are the available flights from New York to London:
1. TransAtlantic TA501: departs 22:00, arrives 10:00+1, $450
2. AirEurope AE303: departs 18:00, arrives 06:00+1, $380
```

Inside, the agent's LLM called `search_flights("New York", "London")`.

**Terminal 3 · Trip Summary**

```text
Destination: London
Weather: The weather in London is currently 15°C, cloudy with occasional rain.

Flights (New York → London):
Here are the available flights from New York to London:
1. TransAtlantic TA501: departs 22:00, arrives 10:00+1, $450
2. AirEurope AE303: departs 18:00, arrives 06:00+1, $380
```

Two independent agents, one combined answer. The orchestrator itself has no LLM: it just routes messages and prints.

**If Terminal 2 isn't running (flights agent down):**

**→ Flights agent :9002 · `GET /.well-known/agent-card.json`**

**✗ Nothing is listening on port 9002**

```text
A2AClientHTTPError: HTTP Error 503: Network communication error fetching agent card from http://127.0.0.1:9002/.well-known/agent-card.json: All connection attempts failed
```

The orchestrator doesn't catch this error, so it stops with a traceback after printing the weather. Start `flights_agent_server.py` in terminal 2 and run it again. Notice the weather agent was unaffected: independent agents fail independently.

**If the route isn't in the data (London to Tokyo):**

**← Task completed · artifact**

```text
Sorry, there are no flights from London to Tokyo. Available routes are: London → Paris, New York → London, Tokyo → Sydney, Paris → Rome, Dubai → Bangkok, New York → Cancun.
```

Inside, the agent's LLM called `search_flights("London", "Tokyo")`, which returned the list of available routes, and relayed it.

#### Both protocols together: A2A outside, MCP inside

In this lab the weather agent keeps its data in a Python dictionary. In a real system it would more likely get weather from an MCP server, which is exactly what you built in Lab 5.6. The two protocols then sit at different layers: **A2A between agents, MCP between each agent and its tools**. The orchestrator doesn't notice the change at all, because the weather agent is opaque.

{{diagram:4}}

*Different layers, no overlap. A2A lets agents collaborate; MCP lets each agent do its own work with tools and data.*

To try it, change only the agent in `weather_agent_server.py`, reusing the `MCPClient` pattern from Lab 5.7. Recent Strands versions accept an `MCPClient` directly in `tools=[...]` and open and close the connection for you:

```pseudo title="weather_agent_server.py · optional change"
// the MCP server from Lab 5.6, started as a child process over stdio
SET SERVER = the path to ../mcp-basics/server.py
SET mcp_client = MCPClient(a function that starts SERVER over stdio, using sys.executable)
CREATE weather_agent = Agent(
    model = BedrockModel(MODEL_ID, REGION)
    name = "Weather Agent"
    description = "Provides current weather information for cities around the world."
    system_prompt = "You are a helpful weather assistant. Be concise and friendly."
    tools = [mcp_client]   // tools now come over MCP instead of @tool
    callback_handler = None
)
```

> **Imported:**
> - `sys` Python standard library: gives `sys.executable`, so the server starts with the same Python.
> - `Path` from `pathlib`, Python standard library: finds `server.py` in the `mcp-basics` folder.
> - `StdioServerParameters` from `mcp`, package mcp: settings for starting the server over stdio.
> - `stdio_client` from `mcp`, package mcp: opens the stdio connection to the server.
> - `MCPClient` from `strands.tools.mcp`: wraps the MCP connection so Strands can use the server's tools.

```python reveal title="weather_agent_server.py · optional change"
import sys
from pathlib import Path
from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

# The MCP server from Lab 5.6, started as a child process over stdio
SERVER = Path(__file__).resolve().parent.parent / "mcp-basics" / "server.py"
mcp_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(command=sys.executable, args=[str(SERVER)]))
)

weather_agent = Agent(
    model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
    name="Weather Agent",
    description="Provides current weather information for cities around the world.",
    system_prompt="You are a helpful weather assistant. Be concise and friendly.",
    tools=[mcp_client],      # tools now arrive over MCP instead of @tool
    callback_handler=None,
)
```

> **The data changes too:**
> The MCP server only knows London, Paris, Tokyo, New York and Bangalore, with shorter descriptions ("15°C, cloudy"). Ask the orchestrator for Bangalore and it now works; ask for Rome and the weather agent will say it has no data. This is an experiment for you to try, not part of the course lab.

> **Extend it yourself:**
> Give the orchestrator an LLM: create a Strands agent whose tools wrap the two remote agents, for example one small `@tool` per agent that calls `send_a2a_message` with that agent's URL. Then it can decide on its own when to check the weather, when to search flights, and even when to call `book_flight`.
