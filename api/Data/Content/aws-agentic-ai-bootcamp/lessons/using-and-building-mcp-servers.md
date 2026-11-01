# Using and building MCP servers

## 5.5 Using and building MCP servers

Two ways to work with servers: use one that already exists, or build your own for your systems.

#### Using pre-built servers

Many ready-made servers exist, from Anthropic, the open-source community and AWS (through the official MCP servers for AWS from AWS Labs). You can connect, say, the GitHub MCP server or a Slack MCP server to an MCP host such as Claude Code, VS Code or Kiro, and every MCP-compatible agent can use their tools.

A concrete example is the **AWS Documentation MCP server**, which exposes tools for searching and reading official AWS documentation. Your code launches it as a local process with `uvx`, creates an MCP client that talks to it over stdio, lists its tools, and hands them to a Strands agent. The agent then answers AWS questions from the docs rather than only from its training. You'll run exactly this in 5.7. You write no AWS-documentation integration code yourself: the server packages that capability as reusable tools.

#### Building your own server

To expose your organisation's tools and data, you build a custom server: use an SDK to define tools (actions) and resources (data), then run it with a chosen transport. Official MCP SDKs exist for many languages, including Python, TypeScript, Java, C# and Go; this course uses Python.

##### FastMCP vs FastAPI

|  | **FastMCP** | **FastAPI** |
| --- | --- | --- |
| What it is | Built specifically for MCP, with MCP-native ways to define tools, resources and prompts | A general-purpose web framework |
| Choose it when | You want an MCP server quickly, with little boilerplate, and the service mainly exposes MCP capabilities | MCP is one part of a bigger service that also has REST APIs, custom auth flows, health checks or dashboards |
| Trade-off | Focused on MCP | More flexibility, but you write more of the MCP plumbing yourself |

> **Think of it like this:**
> FastMCP is a ready-made food-truck kit: perfect when all you want to do is serve one menu, fast. FastAPI is a full restaurant kitchen: more to set up, but it can also run the bar, the bakery and the delivery counter.

##### Using MCP from agent frameworks

Frameworks such as Strands and LangChain act as MCP *clients* (or adapters): they let agents discover and call tools exposed by MCP servers. They don't define the server; they help agents consume MCP capabilities inside a bigger reasoning and orchestration flow.

##### Strands

Strands Agents ships with MCP support built on the official MCP Python SDK (which includes FastMCP). Use Strands for the agent, tool discovery and AWS connections, and FastMCP for the fast, focused tools the agent calls.

##### LangChain

The `langchain-mcp-adapters` library converts MCP tools into standard LangChain tools, so LangChain and LangGraph agents can use any MCP server.

## 5.6 Lab: an MCP server and client

Build a weather server with FastMCP that exposes every MCP primitive, and a client that discovers and uses each one. No LLM, no AWS: just the protocol.

{{diagram:1}}

*One server, one client, every primitive. The client starts the server itself and they talk through pipes: no ports, no HTTP.*

| Primitive | Name | What it is |
| --- | --- | --- |
| Tool | `get_weather(city)` | A function the LLM can call |
| Tool | `list_client_roots()` | Asks the *client* which folders it shared (roots) |
| Resource (template) | `greeting://{name}` | Data the app can read, like a GET endpoint |
| Resource (JSON) | `courses://directory` | A fixed resource with `application/json` content |
| Prompt | `weather_report(city)` | A reusable prompt template |
| Prompt | `generate_study_plan(course, exam_date)` | A template with two arguments |

And the client exposes **roots**: the folders the server is allowed to work in.

#### `server.py`, step by step

```pseudo title="server.py · imports and the server object"
// FastMCP handles the JSON-RPC messages, registration and transport for you
IMPORT json
IMPORT Context and FastMCP from mcp.server.fastmcp
CREATE mcp = a FastMCP server named "WeatherServer", logging at WARNING   // the name is shown during the handshake
```

> **Imported:**
> - `json` Python standard library: turns the course list into JSON text.
> - `Context` from `mcp.server.fastmcp`, package mcp: gives a tool access to the connected client, used to ask for its roots.
> - `FastMCP` from `mcp.server.fastmcp`, package mcp: the high-level helper that builds the MCP server.

```python reveal title="server.py · imports and the server object"
"""
MCP Server — exposes all the MCP primitives over stdio transport:

  * Tools      — get_weather, list_client_roots
  * Resources  — greeting://{name}  and  courses://directory (JSON)
  * Prompts    — weather_report, generate_study_plan

MCP (Model Context Protocol) lets LLM applications discover and call tools,
read resources, and use prompt templates through one standard protocol.

Run:  python client.py   (the client starts this server for you)
"""

import json

# FastMCP: high-level helper for building MCP servers. It handles JSON-RPC
# parsing, registration of tools/resources/prompts, and the transport.
from mcp.server.fastmcp import Context, FastMCP

# The name identifies this server to clients when they connect.
mcp = FastMCP("WeatherServer", log_level="WARNING")
```

`FastMCP` is the high-level API from the official MCP Python SDK. It handles the protocol details for you: JSON-RPC messages, capability negotiation, and generating schemas from your type hints. The name `"WeatherServer"` is how the server introduces itself during the handshake; `log_level="WARNING"` keeps its own logs quiet.

```pseudo title="server.py · tool: get_weather"
// @mcp.tool() registers this function as a tool the LLM can call
DEFINE get_weather(city):   // the docstring becomes the description
    // fake data for the demo, not a real weather API
    SET fake_weather = a lookup of city names to weather text (London, Paris, Tokyo, New York, Bangalore)
    SET result = fake_weather looked up with city in lower case
    IF result is found THEN
        RETURN "Weather in " + city + ": " + result
    RETURN "Sorry, no weather data available for '" + city + "'."
```

```python reveal title="server.py · tool: get_weather"
# --- Tool: get_weather ---------------------------------------------------
# Tools are functions an LLM can call. @mcp.tool() registers the function so
# it appears in list_tools() and can be invoked with call_tool(). The
# docstring becomes the description the LLM sees.

@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    # Fake data for demo purposes — a real server would call a weather API
    fake_weather = {
        "london": "15°C, cloudy",
        "paris": "18°C, sunny",
        "tokyo": "22°C, humid",
        "new york": "12°C, windy",
        "bangalore": "26°C, pleasant with light showers",
    }
    result = fake_weather.get(city.lower())
    if result:
        return f"Weather in {city}: {result}"
    return f"Sorry, no weather data available for '{city}'."
```

`@mcp.tool()` registers the function so it appears in `tools/list` and can be run with `tools/call`. Just like Strands' `@tool`, the type hints become the input schema and the docstring becomes the description. The data is fake on purpose (including Bangalore, which the Strands lab asks about); a real server would call a weather API.

```pseudo title="server.py · tool that uses roots"
// the server asks the connected client for its roots
DEFINE list_client_roots(ctx):   // ctx gives access to the client session
    CALL ctx.session.list_roots() and WAIT for the client's answer
    IF the client shared no roots THEN
        RETURN "The client did not share any roots."
    RETURN each root as "name: uri", one per line
```

```python reveal title="server.py · tool that uses roots"
# --- Tool that uses a client capability: roots ---------------------------
# Roots are folders/URIs the *client* says the server may work within.
# A server can ask the client for its roots at any time.

@mcp.tool()
async def list_client_roots(ctx: Context) -> str:
    """List the workspace roots the connected client has shared with this server."""
    result = await ctx.session.list_roots()
    if not result.roots:
        return "The client did not share any roots."
    return "\n".join(f"{root.name}: {root.uri}" for root in result.roots)
```

This tool shows the protocol running *backwards*. FastMCP injects a `Context` object (it is hidden from the input schema, which is why `list_client_roots` shows no arguments in `tools/list`); `ctx.session.list_roots()` sends a `roots/list` request from the server to the client and waits for the answer. Because it waits for a round trip to the client over the pipes, the function is `async`.

```pseudo title="server.py · resource template: greeting"
// a resource is read-only data, matched by a URI template
DEFINE get_greeting(name):   // greeting://{name} fills in name
    RETURN "Hello, " + name + "! Welcome to the WeatherServer."
```

```python reveal title="server.py · resource template: greeting"
# --- Resource: greeting ---------------------------------------------------
# Resources are data an LLM application can read (like GET endpoints).
# "greeting://{name}" is a URI template: read_resource("greeting://Developer")
# fills in {name}. Use resources for data, tools for actions.

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Return a personalized greeting."""
    return f"Hello, {name}! Welcome to the WeatherServer."
```

Resources are read-only data endpoints, like GET requests in a REST API. Because the URI contains `{name}`, this is a **template**: reading `greeting://Developer` calls the function with `name="Developer"`.

```pseudo title="server.py · resource: course directory (JSON)"
// a fixed URI, with a name and a JSON mime type
SET COURSES = a list of three courses, each with course, instructor and weeks
DEFINE course_directory():   // served at courses://directory
    RETURN COURSES as JSON text
```

```python reveal title="server.py · resource: course directory (JSON)"
# --- Resource: course directory (structured JSON) -------------------------
# A fixed URI with a MIME type tells the client how to interpret the content.

COURSES = [
    {"course": "Machine Learning", "instructor": "Dr. Rao", "weeks": 12},
    {"course": "Agentic AI on AWS", "instructor": "Shivank Agrawal", "weeks": 8},
    {"course": "Data Engineering", "instructor": "Ms. Iyer", "weeks": 10},
]

@mcp.resource(
    "courses://directory",
    name="courseDirectory",
    title="Course Directory",
    description="List of courses and instructors in a program",
    mime_type="application/json",
)
def course_directory() -> str:
    return json.dumps(COURSES, indent=2)
```

A fixed URI with a name, title, description and `mime_type="application/json"`, the same shape as the resource description in 5.3, with a custom `courses://` URI instead of a file path. The function returns the course list as JSON text.

```pseudo title="server.py · prompts"
// prompts are reusable message templates the client fills in
DEFINE weather_report(city):
    RETURN "Please provide a detailed weather report for " + city + ", including temperature, humidity, and forecast."
DEFINE generate_study_plan(course, exam_date):   // title: Generate Study Plan
    RETURN "Create a week-by-week study plan for the course '" + course + "'. The exam is on " + exam_date + ". Include revision weeks, practice tests, and one concrete goal per week."
```

```python reveal title="server.py · prompts"
# --- Prompts ---------------------------------------------------------------
# Prompts are reusable templates. Clients call get_prompt(name, arguments)
# and get back ready-to-send messages.

@mcp.prompt()
def weather_report(city: str) -> str:
    """Generate a prompt asking for a weather report."""
    return f"Please provide a detailed weather report for {city}, including temperature, humidity, and forecast."

@mcp.prompt(title="Generate Study Plan")
def generate_study_plan(course: str, exam_date: str) -> str:
    """Create a personalized study plan for a student based on their course and exam date."""
    return (
        f"Create a week-by-week study plan for the course '{course}'. "
        f"The exam is on {exam_date}. Include revision weeks, practice tests, "
        "and one concrete goal per week."
    )
```

`@mcp.prompt()` registers reusable templates. A client calls `get_prompt("weather_report", {"city": "Tokyo"})` and gets back ready-to-send messages. `generate_study_plan` is the lab's version of the study-plan template from 5.3, with a `title`.

```pseudo title="server.py · start"
// stdio: read requests from stdin, write replies to stdout
IF this file is run directly THEN
    RUN mcp.run(transport="stdio")   // the client starts this script as a subprocess
```

```python reveal title="server.py · start"
# --- Start the server ------------------------------------------------------
# "stdio" = read JSON-RPC messages from stdin, write responses to stdout.
# The client spawns this script as a subprocess and talks to it through pipes.

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

stdio means: read JSON-RPC messages from standard input and write responses to standard output. The server can connect to an MCP host (Claude Code, Kiro) or to your own client, which is next.

#### `client.py`, step by step

```pseudo title="client.py · imports"
// starts server.py over stdio and exercises every primitive
IMPORT asyncio, json, sys
IMPORT Path from pathlib
IMPORT mcp.types as types
IMPORT ClientSession and StdioServerParameters from mcp
IMPORT stdio_client from mcp.client.stdio
SET HERE = the folder that holds this file, as a full path
```

> **Imported:**
> - `asyncio` Python standard library: runs the async code with `asyncio.run`.
> - `json` Python standard library: reads the JSON text of the course resource back into data.
> - `sys` Python standard library: gives `sys.executable`, the Python that runs the client, so the server uses the same one.
> - `Path` from `pathlib`, Python standard library: works out the lab folder from this file's location.
> - `mcp.types` (as `types`) package mcp, the MCP Python SDK: the protocol data types, used to describe roots.
> - `ClientSession` from `mcp`, package mcp: the MCP client that speaks the protocol for you.
> - `StdioServerParameters` from `mcp`, package mcp: settings that tell the client how to start the server.
> - `stdio_client` from `mcp.client.stdio`, package mcp: the transport that starts the server process and manages its pipes.

```python reveal title="client.py · imports"
"""
MCP Client — starts server.py over stdio and exercises every MCP primitive:
tools, resources, prompts, and roots.

Run:  python client.py
"""

import asyncio
import json
import sys
from pathlib import Path

import mcp.types as types

# ClientSession: the MCP protocol session (initialize, list, call, ...)
# StdioServerParameters: how to start the server subprocess
from mcp import ClientSession, StdioServerParameters

# stdio_client: starts the server process and returns read/write streams
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
```

| Import | Its job |
| --- | --- |
| `ClientSession` | The high-level MCP client that speaks the protocol for you |
| `StdioServerParameters` | Settings that tell the client how to start the server |
| `stdio_client` | The transport: starts the subprocess and manages its stdin/stdout pipes |
| `mcp.types` | Protocol data types, used here to describe roots |

```pseudo title="client.py · roots callback"
// the client decides which folders the server may use
DEFINE list_roots(context):   // answers when the server asks for roots
    RETURN a ListRootsResult with one root:
        uri = this lab folder, as a file:// address
        name = "Course workspace"
```

```python reveal title="client.py · roots callback"
# --- Roots -----------------------------------------------------------------
# The client decides which folders the server may work within. When the
# server asks (list_roots), this callback answers.

async def list_roots(context) -> types.ListRootsResult:
    return types.ListRootsResult(
        roots=[
            types.Root(uri=HERE.as_uri(), name="Course workspace"),
        ]
    )
```

The client decides which folders the server may use. When the server asks (through `list_client_roots`), this callback answers with one root: the lab folder, named "Course workspace". `HERE.as_uri()` turns the folder path into a `file://` URI.

```pseudo title="client.py · connect, handshake, discover"
DEFINE main():   // the async entry point
    SET server_params = run python server.py as a subprocess, using the same Python
    START stdio_client(server_params) to get the read and write streams   // starts the server
        CREATE ClientSession(streams, list_roots_callback=list_roots)
            CALL session.initialize()   // agree on protocol version and capabilities
            // 1. Discover tools
            CALL session.list_tools() and PRINT each tool name and description
            // 2. Discover resources, then resource templates
            CALL session.list_resources() and PRINT each one
            CALL session.list_resource_templates() and PRINT each one
            // 3. Discover prompts
            CALL session.list_prompts() and PRINT each prompt with its arguments
```

```python reveal title="client.py · connect, handshake, discover"
async def main():
    # Start "python server.py" as a subprocess. sys.executable is the same
    # Python that runs this client, so the server sees the same packages.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(HERE / "server.py")],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream, list_roots_callback=list_roots) as session:
            # Required first step: exchange protocol version and capabilities
            await session.initialize()

            # --- 1. Discover tools ----------------------------------------
            tools = await session.list_tools()
            print("=== Available Tools ===")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # --- 2. Discover resources ------------------------------------
            # Fixed resources and URI templates are listed separately.
            print("\n=== Available Resources ===")
            resources = await session.list_resources()
            for r in resources.resources:
                print(f"  - {r.uri} ({r.mimeType}): {r.description}")
            templates = await session.list_resource_templates()
            for rt in templates.resourceTemplates:
                print(f"  - {rt.uriTemplate}: {rt.description}")

            # --- 3. Discover prompts --------------------------------------
            print("\n=== Available Prompts ===")
            prompts = await session.list_prompts()
            for p in prompts.prompts:
                args = ", ".join(a.name for a in (p.arguments or []))
                print(f"  - {p.name}({args}): {p.description}")
```

1. a `StdioServerParameters(...)` Doesn't start anything yet. It says: when you connect, run `server.py` with the same Python (`sys.executable`), so the server sees the same packages.
2. b `async with stdio_client(...)` Starts the server subprocess and hands back raw read/write streams. The `async with` blocks guarantee clean-up: streams closed, process stopped, even if something fails. That's the **shutdown** stage of the lifecycle.
3. c `ClientSession(..., list_roots_callback=list_roots)` and `initialize()` Wraps the streams in the MCP protocol and performs the handshake: versions and capabilities are exchanged. Passing the roots callback is what tells the server "this client supports roots".
4. d Discovery `list_tools()`, `list_resources()`, `list_resource_templates()` and `list_prompts()` ask the server "what do you offer?". Fixed resources and URI templates are listed separately.

```pseudo title="client.py · call tools, read resources"
// 4. call a tool with a known city
CALL get_weather with city "London" and PRINT the text of the result
// 5. call a tool with a city that has no data
CALL get_weather with city "Berlin" and PRINT the text of the result
// 6. read a templated resource
READ greeting://Developer and PRINT its text
// 7. read the JSON resource
READ courses://directory
    SET courses = the text, parsed from JSON
    FOR EACH course in courses PRINT its name, instructor and weeks
```

```python reveal title="client.py · call tools, read resources"
            # --- 4. Call a tool (known city) ------------------------------
            print("\n=== Calling get_weather('London') ===")
            result = await session.call_tool("get_weather", {"city": "London"})
            print(f"  Result: {result.content[0].text}")

            # --- 5. Call a tool (unknown city) ----------------------------
            print("\n=== Calling get_weather('Berlin') ===")
            result = await session.call_tool("get_weather", {"city": "Berlin"})
            print(f"  Result: {result.content[0].text}")

            # --- 6. Read a templated resource -----------------------------
            print("\n=== Reading greeting://Developer ===")
            resource = await session.read_resource("greeting://Developer")
            print(f"  Result: {resource.contents[0].text}")

            # --- 7. Read a JSON resource ----------------------------------
            print("\n=== Reading courses://directory ===")
            resource = await session.read_resource("courses://directory")
            courses = json.loads(resource.contents[0].text)
            for c in courses:
                print(f"  - {c['course']} — {c['instructor']} ({c['weeks']} weeks)")
```

`call_tool` sends `tools/call` with a name and arguments; `result.content` is a list of content blocks, so `[0].text` is the first block's text. Berlin isn't in the fake data, so you'll see the polite "no data" message: tools return errors as normal results. `read_resource` sends `resources/read`; the server matches `greeting://Developer` against the template and fills in the name. The course directory comes back as JSON text, which `json.loads` turns into Python data.

```pseudo title="client.py · prompts, roots, entry point"
// 8. get the weather_report prompt for Tokyo
CALL get_prompt("weather_report", city "Tokyo") and PRINT the message text
CALL get_prompt("generate_study_plan", course "Machine Learning", exam_date "2026-05-10") and PRINT the message text
// 9. roots: the server asks the client
CALL list_client_roots and PRINT the result
IF this file is run directly THEN
    RUN asyncio.run(main())   // runs main() and closes the event loop when done
```

```python reveal title="client.py · prompts, roots, entry point"
            # --- 8. Get prompts -------------------------------------------
            print("\n=== Getting weather_report prompt ===")
            prompt = await session.get_prompt("weather_report", {"city": "Tokyo"})
            print(f"  Result: {prompt.messages[0].content.text}")

            print("\n=== Getting generate_study_plan prompt ===")
            prompt = await session.get_prompt(
                "generate_study_plan", {"course": "Machine Learning", "exam_date": "2026-05-10"}
            )
            print(f"  Result: {prompt.messages[0].content.text}")

            # --- 9. Roots: the server asks the client ---------------------
            print("\n=== Calling list_client_roots ===")
            result = await session.call_tool("list_client_roots", {})
            print(f"  Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

`get_prompt` fetches a template with arguments; the server fills it in and returns a list of messages. In a real app you'd send those messages to an LLM. The final call triggers the roots round trip. `asyncio.run(main())` starts an event loop (the scheduler that runs `async` code and switches between tasks while they wait), runs `main()`, and closes the loop when done.

#### Run it

```pseudo title="terminal"
RUN pip install -r requirements.txt
RUN python client.py        // the client starts server.py automatically
```

```bash reveal title="terminal"
pip install -r requirements.txt
python client.py        # starts server.py automatically
```

```text title="outputreal output; your folder path will differ"
=== Available Tools ===
  - get_weather: Get the current weather for a given city.
  - list_client_roots: List the workspace roots the connected client has shared with this server.

=== Available Resources ===
  - courses://directory (application/json): List of courses and instructors in a program
  - greeting://{name}: Return a personalized greeting.

=== Available Prompts ===
  - weather_report(city): Generate a prompt asking for a weather report.
  - generate_study_plan(course, exam_date): Create a personalized study plan for a student based on their course and exam date.

=== Calling get_weather('London') ===
  Result: Weather in London: 15°C, cloudy

=== Calling get_weather('Berlin') ===
  Result: Sorry, no weather data available for 'Berlin'.

=== Reading greeting://Developer ===
  Result: Hello, Developer! Welcome to the WeatherServer.

=== Reading courses://directory ===
  - Machine Learning — Dr. Rao (12 weeks)
  - Agentic AI on AWS — Shivank Agrawal (8 weeks)
  - Data Engineering — Ms. Iyer (10 weeks)

=== Getting weather_report prompt ===
  Result: Please provide a detailed weather report for Tokyo, including temperature, humidity, and forecast.

=== Getting generate_study_plan prompt ===
  Result: Create a week-by-week study plan for the course 'Machine Learning'. The exam is on 2026-05-10. Include revision weeks, practice tests, and one concrete goal per week.

=== Calling list_client_roots ===
  Result: Course workspace: file:///…/mcp-basics
```

Notice that the client never imported the server's functions. Everything it knows (names, descriptions, argument lists) came over the protocol at run time. That's dynamic discovery.

> **Want a visual tool?:**
> If you have Node.js installed, run `npx @modelcontextprotocol/inspector python server.py` in the `mcp-basics` folder. The MCP Inspector opens in your browser and lets you click through the server's tools, resources and prompts.

## 5.7 Lab: Strands agents with MCP tools

Now add the LLM. A Strands agent gets its tools from MCP servers, first from your own server, then from AWS's documentation server, without knowing anything about those tools in advance.

{{diagram:2}}

*Same pattern, any server. Swap the command that starts the server and the agent gets a completely different toolbox, with no other code changes.*

Both scripts follow the same pattern:

```pseudo title="the pattern"
SET mcp_client = MCPClient(a function that starts an MCP server over stdio)   // opened later, by Strands
with mcp_client:   // starts the server and keeps the session open
    SET tools = mcp_client.list_tools_sync()   // discover the server's tools
    CREATE agent = Agent(tools = tools)
    ASK agent a question   // the model decides when to call each tool
```

```python reveal title="the pattern"
mcp_client = MCPClient(lambda: stdio_client(StdioServerParameters(command=..., args=[...])))

with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(tools=tools)
    agent("...")
```

#### Script 1: an agent using your own MCP server

```pseudo title="agent_with_local_mcp.py"
// a Strands agent whose tools come from an MCP server
SET MODEL_ID = the BEDROCK_MODEL_ID environment variable, or the default Claude Sonnet 4.6 model
SET REGION = AWS_REGION, else AWS_DEFAULT_REGION, else us-east-1
SET SERVER = the path to ../mcp-basics/server.py
SET mcp_client = MCPClient(a function that starts SERVER over stdio, using sys.executable)   // opened later, when Strands is ready
with mcp_client:   // starts the server and keeps the session open
    SET tools = mcp_client.list_tools_sync()   // discover the tools over MCP
    PRINT the name of each tool
    CREATE agent = Agent(model = BedrockModel(MODEL_ID, REGION), tools = tools)
    ASK agent "I'm flying from Bangalore to London tomorrow. What's the weather like in both cities?"
    PRINT a blank line
```

> **Imported:**
> - `os` Python standard library: reads the model ID and region from environment variables.
> - `sys` Python standard library: gives `sys.executable`, so the server starts with the same Python.
> - `Path` from `pathlib`, Python standard library: finds `server.py` in the sibling `mcp-basics` folder.
> - `StdioServerParameters` from `mcp`, package mcp: settings for starting the server over stdio.
> - `stdio_client` from `mcp`, package mcp: opens the stdio connection to the server.
> - `Agent` from `strands`: the agent that decides when to call the tools.
> - `BedrockModel` from `strands.models.bedrock`: the Amazon Bedrock model the agent thinks with.
> - `MCPClient` from `strands.tools.mcp`: wraps the MCP connection so Strands can use the server's tools.

```python reveal title="agent_with_local_mcp.py"
"""
A Strands agent that gets its tools from an MCP server.

It starts the server from ../mcp-basics/server.py over stdio, discovers its
tools, and lets the model decide when to call them. The agent code knows
nothing about the weather tool in advance — it all comes over MCP.

Run:  python agent_with_local_mcp.py
"""

import os
import sys
from pathlib import Path

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

SERVER = Path(__file__).resolve().parent.parent / "mcp-basics" / "server.py"

# MCPClient takes a function that opens the transport. Here: spawn the server.
mcp_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(command=sys.executable, args=[str(SERVER)]))
)

with mcp_client:
    tools = mcp_client.list_tools_sync()
    print("Tools discovered over MCP:", [t.tool_name for t in tools])

    agent = Agent(model=BedrockModel(model_id=MODEL_ID, region_name=REGION), tools=tools)
    agent("I'm flying from Bangalore to London tomorrow. What's the weather like in both cities?")
    print()
```

1. a `SERVER = …/"mcp-basics"/"server.py"` Reuses the server you just built. `Path(__file__).resolve().parent.parent` climbs from this script's folder to the section folder.
2. b `MCPClient(lambda: stdio_client(...))` Strands' MCP client. It takes a *function* that opens the transport (that's what the `lambda` is), so Strands can open the connection when it's ready, on its own background thread.
3. c `with mcp_client:` Starts the server and keeps the MCP session open for the whole block. The agent must be used *inside* it, because its tools are live connections to the server.
4. d `list_tools_sync()` Discovers the server's tools and wraps each as a Strands tool. `t.tool_name` gives each one's name. Pass the list straight to `Agent(tools=...)`.

```text title="outputillustrative wording"
Tools discovered over MCP: ['get_weather', 'list_client_roots']
I'll check the weather in both cities for you.
Tool #1: get_weather
Tool #2: get_weather
Here's the weather for your trip:

Bangalore: 26°C, pleasant with light showers. Keep an umbrella handy on the way to the airport.
London: 15°C and cloudy. Pack a light jacket for when you land.
```

The agent's code never mentioned weather. It learned about `get_weather` over MCP, and Claude decided to call it twice, once per city.

#### Script 2: an agent using the AWS Documentation MCP server

```pseudo title="agent_with_aws_docs_mcp.py"
// a Strands agent that answers from the AWS documentation server
SET MODEL_ID = the BEDROCK_MODEL_ID environment variable, or the default Claude Sonnet 4.6 model
SET REGION = AWS_REGION, else AWS_DEFAULT_REGION, else us-east-1
IF the uvx command is not installed THEN
    STOP with the message "uvx not found. Install uv first: pip install uv"
SET mcp_client = MCPClient(a function that runs "uvx awslabs.aws-documentation-mcp-server@latest" over stdio, passing your environment with FASTMCP_LOG_LEVEL = ERROR, startup_timeout = 120)   // the first run downloads the package
with mcp_client:   // starts the server and keeps the session open
    SET tools = mcp_client.list_tools_sync()   // discover the documentation tools
    PRINT the name of each tool
    CREATE agent = Agent(model = BedrockModel(MODEL_ID, REGION), tools = tools, system_prompt = "Answer AWS questions using the documentation tools. Cite the doc URLs you used.")
    ASK agent "What is AWS Lambda, and what is the maximum timeout for a Lambda function?"
    PRINT a blank line
```

> **Imported:**
> - `os` Python standard library: reads the model settings and passes your environment on to the server.
> - `shutil` Python standard library: its `which` function checks that `uvx` is installed.
> - `StdioServerParameters` from `mcp`, package mcp: settings for starting the server (command, arguments and environment).
> - `stdio_client` from `mcp`, package mcp: opens the stdio connection to the server.
> - `Agent` from `strands`: the agent that decides when to call the documentation tools.
> - `BedrockModel` from `strands.models.bedrock`: the Amazon Bedrock model the agent uses.
> - `MCPClient` from `strands.tools.mcp`: wraps the MCP connection so Strands can use the server's tools.

```python reveal title="agent_with_aws_docs_mcp.py"
"""
A Strands agent connected to the AWS Documentation MCP server.

The AWS Labs documentation server (https://github.com/awslabs/mcp) lets the
agent search and read official AWS docs, so its answers come from current
documentation instead of only the model's training data.

Prerequisite: `uv` installed (it provides the `uvx` command that downloads and
runs the server on demand).

Run:  python agent_with_aws_docs_mcp.py
"""

import os
import shutil

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

if shutil.which("uvx") is None:
    raise SystemExit("`uvx` not found. Install uv first: pip install uv")

# Create MCP client
mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"],
            env={**os.environ, "FASTMCP_LOG_LEVEL": "ERROR"},
        )
    ),
    startup_timeout=120,  # first run downloads the server package
)

# Use with agent
with mcp_client:
    tools = mcp_client.list_tools_sync()
    print("Tools from the AWS Documentation MCP server:", [t.tool_name for t in tools])

    agent = Agent(
        model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
        tools=tools,
        system_prompt="Answer AWS questions using the documentation tools. Cite the doc URLs you used.",
    )
    agent("What is AWS Lambda, and what is the maximum timeout for a Lambda function?")
    print()
```

| Line | Why it's there |
| --- | --- |
| `shutil.which("uvx")` | The server is started with **uvx**, which comes with `uv` (in this lab's `requirements.txt`). The check fails early with a clear message if it's missing. |
| `args=["awslabs.aws-documentation-mcp-server@latest"]` | Tells `uvx` to download (first time) and run the latest AWS Labs documentation server. |
| `env={**os.environ, "FASTMCP_LOG_LEVEL": "ERROR"}` | Passes your environment through to the server, and quiets its logs. |
| `startup_timeout=120` | The first run downloads the server package, which can take 30 seconds or more and exceed Strands' default 30-second startup timeout. |
| `system_prompt=…"Cite the doc URLs you used."` | Asks the agent to answer from the documentation tools and show its sources. |

```text title="outputillustrative; tool names depend on the server version"
Tools from the AWS Documentation MCP server: ['read_documentation', 'search_documentation', 'recommend']
Tool #1: search_documentation
Tool #2: read_documentation
AWS Lambda is a serverless compute service that runs your code in response to events
and automatically manages the underlying compute resources.

The maximum timeout for a Lambda function is 900 seconds (15 minutes).

Sources:
- https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html
```

> **Why this matters:**
> Model knowledge has a cut-off date; documentation doesn't. By plugging in a documentation server, the agent's answers come from current docs, and you wrote zero integration code for it.
