# Why agents need protocols

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

An agent or host app MCP client, requests MCP server, tools, responses Protocol layer, A2A LLM, prompts, the user Problems, limits, blocked

Section 5: How agents talk

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 5 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/How-agents-talk-main.zip)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### How agents talk

Section 5. Two open protocols do for agents what USB and HTTP did for computers. **MCP** plugs an agent into tools and data that live in other programs. **A2A** lets independent agents find each other and work together. You'll build both.

Folder `section-05-mcp-and-a2a` Labs `mcp-basics` `mcp-with-strands-agent` `a2a-travel-agents` Model: Claude Sonnet 4.6 on Amazon Bedrock

{{diagram:1}}

*Two layers of interoperability. A2A connects agents to agents; MCP connects each agent to its tools and data. You'll build each layer in its own lab.*

## 5.0 Why agents need protocols

You've built agents, given them tools and memory, and organised them into teams. The next step is communication: how agents connect reliably to outside tools, data and other agents, in a structured, reusable way.

As agents get more capable, this communication layer becomes critical. Without a standard, every new tool, service or partner agent means more custom integration code, more maintenance and more complexity. Two protocols tackle this from different directions:

> **Model Context Protocol (MCP):**
> Standardises how agents and models connect to **tools, resources and prompt templates**, so an agent can discover and use outside capabilities without hard-coding every integration.

> **Agent-to-Agent protocol (A2A):**
> Standardises how **agents talk to other agents**, so specialised agents can collaborate across teams and systems while keeping their internals private.

> **Think of it like this:**
> MCP is the universal charging port: any device that has it works with any charger that has it, and nobody needs a drawer full of special cables. A2A is more like the way two companies email each other: each keeps its own staff and processes private, but they agree on how a request looks, how to reply, and how to follow up.

#### What you'll learn here

1. MCP: standardising the interface between models and tools
2. How MCP works: host, client, server, data sources, and the protocol layer
3. The difference between a host and an MCP client
4. Transports, lifecycle and authorisation
5. MCP server and client features
6. FastMCP vs FastAPI, pre-built and custom servers
7. Hands-on: an MCP server and client in Python with FastMCP, then Strands agents that use MCP tools
8. The A2A protocol: architecture, protocol bindings and communication model
9. Hands-on: a travel assistant built from Strands agents talking A2A

#### Before you start

1. 1 A working Strands setup from earlier sections
2. 2 Basic Python functions and classes The MCP lab also uses `async`/`await`; you met it in Section 2.
3. 3 AWS credentials with Amazon Bedrock access Needed for the Strands + MCP lab and the A2A lab (Claude Sonnet 4.6, override with `BEDROCK_MODEL_ID`). The MCP basics lab needs no AWS and no LLM at all.
4. 4 An IDE and three terminal windows VS Code, Kiro or Claude Code. The A2A lab runs three programs side by side.
5. 5 REST and JSON (helpful, not required)

| Folder | What it shows | On this page |
| --- | --- | --- |
| `mcp-basics/` | An MCP server exposing every primitive (tools, resources, prompts, roots) and a client that uses them. No LLM involved. | 5.6 |
| `mcp-with-strands-agent/` | Strands agents that get their tools from MCP servers: our local server, and the AWS Documentation MCP server | 5.7 |
| `a2a-travel-agents/` | Two A2A agent servers (weather, flights) and an orchestrator that discovers and calls them | 5.11 |

```pseudo title="terminal"
// MCP basics: no AWS and no LLM needed
RUN cd mcp-basics, then pip install -r requirements.txt
RUN python client.py   // the client starts server.py itself

// Strands + MCP
RUN cd ../mcp-with-strands-agent, then pip install -r requirements.txt
RUN python agent_with_local_mcp.py
RUN python agent_with_aws_docs_mcp.py

// A2A: three terminals
RUN cd ../a2a-travel-agents, then pip install -r requirements.txt
RUN python weather_agent_server.py      // terminal 1
RUN python flights_agent_server.py      // terminal 2
RUN python travel_orchestrator.py       // terminal 3
```

```bash reveal title="terminal"
# MCP basics (no AWS needed)
cd mcp-basics && pip install -r requirements.txt && python client.py

# Strands + MCP
cd ../mcp-with-strands-agent && pip install -r requirements.txt
python agent_with_local_mcp.py
python agent_with_aws_docs_mcp.py

# A2A — three terminals
cd ../a2a-travel-agents && pip install -r requirements.txt
python weather_agent_server.py      # terminal 1
python flights_agent_server.py      # terminal 2
python travel_orchestrator.py       # terminal 3
```

> **Library versions matter here:**
> The MCP labs pin `mcp[cli]>=1.23.0,<2.0.0` because version 2 renamed FastMCP and changed client APIs; this code targets the 1.x line. The A2A lab pins `a2a-sdk>=0.3.0,<0.4.0` and installs Strands with its `[a2a]` extra.

|  | MCP | A2A |
| --- | --- | --- |
| Purpose | Connect an LLM app to tools and data | Connect agents to other agents |
| Transport | stdio, Streamable HTTP | HTTP (JSON-RPC, SSE) |
| Discovery | `list_tools()`, `list_resources()`, `list_prompts()` | Agent card at `/.well-known/agent-card.json` |
| Who has the LLM | The client side | Both sides; each agent has its own |
| Messages | Structured calls (tool name + arguments) | Natural-language messages and tasks |

> **In one line:**
> **MCP is LLM ↔ tool. A2A is agent ↔ agent.**

## 5.1 MCP: why tools need a standard

As agents grow, managing dozens or hundreds of tools gets hard. What if an agent could discover tools at run time, including tools built by other teams, without hard-coding each one? That's what the **Model Context Protocol** is for.

Agents need to reach APIs, databases and developer platforms. Without a standard, every model needs a custom integration for every tool, which quickly gets complex, costly and hard to maintain. A standard protocol gives one common interface for tool use: less integration work, better interoperability, and easier growth as new tools and models arrive.

{{diagram:2}}

*N × M becomes N + M. Each model connects to MCP once and each tool connects to MCP once. Adding a fourth model or tool adds one connection, not three.*

Try it

##### Count the integrations

AI apps or models (N) = 3 3

Tools and systems (M) = 3 3

**Traditional (default: 3 apps, 3 tools):**

**3 × 3 = 9 custom integrations** to build, test and maintain. Every new app has to be wired to every tool again, and one API change in a tool breaks 3 integrations. Try adding one more tool: that's 3 more connectors.

**With MCP (default: 3 apps, 3 tools):**

**3 + 3 = 6 MCP implementations.** Each app builds one MCP client, each tool ships one MCP server, and any app can use any tool. That's 3 fewer pieces of glue code than the 9 custom integrations, and adding a tool costs exactly one server.

{{diagram:3}}

#### What problem does MCP solve?

Imagine an enterprise agent that must work with your CRM, inventory database, email, calendar, document storage and more. Traditionally you'd write custom integration code for each system, keep it working as each system changes, handle authentication and authorisation for every one, juggle different API formats and conventions, and update the agent whenever a new system is added. That siloed approach leads to **fragmented app development**: every integration built from scratch, with no shared standard.

Worse, each AI app builds its *entire* stack on its own:

{{diagram:4}}

*Three apps, three of everything. If app 1 solves a data-access problem, apps 2 and 3 can't benefit; bugs are fixed three times; the same task may behave differently in each app.*

This doesn't scale. It's slow, error-prone, and couples your agent tightly to every system it touches. MCP replaces it with one standard layer that every AI app shares, a common protocol for tool calls and data access. The benefits:

##### Dynamic tool discovery

Your agent automatically sees every tool on the servers it's connected to.

##### No integration code

Connect to new tool sources without writing custom adapters.

##### Automatic updates

When a server adds or changes tools, your agent sees the change.

##### Unified interface

Tools from AWS, GitHub or your internal systems all work the same way.

##### Flexible deployment

MCP servers can run locally on your machine or remotely in the cloud.

MCP is a universal adapter for agents, much like USB for devices. Through it, models reach databases (such as DynamoDB), CRMs, calendars, code repositories (GitHub), messaging (Slack) and document storage (Google Drive), all through one integration layer:

{{diagram:5}}

*A tangle vs a hub. Without MCP, agents maintain a separate integration for each tool. With MCP, one standard, reusable connection layer reaches all of them the same way.*

## 5.2 How MCP works

MCP sets up a standard protocol between your agent and tool providers, much as USB set a universal standard for connecting devices to computers.

{{diagram:6}}

*Four parts, one chain. The host never talks to a database directly; it goes through a client and a server that both speak MCP.*

1. 1 Host The AI application or agent that needs to get things done: answer questions, retrieve information, use tools. It doesn't connect to outside systems directly; it talks to an MCP client.
2. 2 MCP client (tool consumer) Built into your agent. It connects to an MCP server, discovers the available tools and handles the protocol. When your agent needs a tool, the client calls the right server with the required parameters.
3. 3 MCP server (tool provider) A service that exposes a catalogue of tools with descriptions, parameters and capabilities. For example, AWS Labs publishes an MCP server for AWS documentation, GitHub publishes servers for repository operations, and you can build your own for internal systems.
4. 4 Data sources The real databases, APIs, files or enterprise systems behind the server. The server fetches what's needed and sends results back through the client to the host.

These parts work through one standardised communication layer, the core idea of MCP. Instead of every host and tool provider inventing its own integration, MCP defines one protocol for how clients and servers discover capabilities, exchange requests and return results. That shared protocol is what makes it scalable, reusable and easier to maintain.

#### The difference between a host and an MCP client

An MCP client never runs on its own. It's created and managed by a **host** application, such as a code editor, an AI assistant or a browser extension. The host owns the user experience: the interface, session memory and prompt orchestration. It can run **several clients at once**, each connected to a different server.

Each **MCP client**, in contrast, is a protocol-level component with a **one-to-one** connection to a single **MCP server**. It discovers that server's tools, resources and prompts, gathers context for the model, and asks the user for missing information when needed. In short: **the host is what users interact with; the client lets the host talk to one specific server.**

{{diagram:7}}

*One host, many clients, one server each. Keeping every connection one-to-one keeps each simple and isolated, while the host as a whole reaches many services.*

> **Remember it this way:**
> The **host** is the application layer (UI, workflows, user interaction). The **client** is the integration layer inside the host that speaks MCP. The host orchestrates; each client talks to exactly one server.

#### Transports, lifecycle and authorisation

A client and its server exchange messages over a **transport**. MCP messages use **JSON-RPC 2.0** and must be UTF-8 encoded. The client and server define *what* is said; the transport defines *how* it travels. There are two standard transports plus a custom option, all for the same job in different deployments:

{{diagram:8}}

*Same conversation, different wires. The JSON-RPC messages are identical; only the way they travel changes.*

| Transport | Best for | Example |
| --- | --- | --- |
| **stdio** (standard input/output) | Local integrations where client and server run on the same machine. Simple, direct, lightweight, like command-line programs piping data to each other. | An agent running on your laptop, as in this section's labs |
| Streamable HTTP | Web-based or remote servers. Uses HTTP and can stream results incrementally with **server-sent events (SSE)**. (It replaced the older stand-alone SSE transport.) | A live assistant receiving updates as they happen |
| Custom | When the built-in options don't fit | An enterprise team using **gRPC** for high performance |

##### Managing the lifecycle

**Lifecycle** management covers how a client and server start, maintain and end a connection: agreeing on protocol versions, learning each other's capabilities, and managing session state. Three stages:

{{diagram:9}}

*Handshake, conversation, goodbye. Nothing else may happen until the handshake agrees a protocol version and capabilities.*

1. 1 Initialisation Client and server agree on the protocol version and capabilities. Example: an agent connecting to a server for a company database performs the handshake, and the server confirms which features it offers, for example tools such as a `run_query` tool.
2. 2 Operation Normal protocol traffic. The agent asks for customer records; the server processes the requests and returns structured responses.
3. 3 Shutdown The client closes the connection gracefully, letting ongoing operations finish and releasing resources.

Watch the wire

##### A real MCP conversation, message by message

These are the real JSON-RPC messages that go over the pipes when you run this section's `client.py` against `server.py` (captured from a real run, lightly shortened).

not connected

**Client → server · `initialize` · request id 0**

```json
{
  "jsonrpc": "2.0", "id": 0, "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": { "roots": { "listChanged": true } },
    "clientInfo": { "name": "mcp", "version": "0.1.0" }
  }
}
```

`session.initialize()` sends this. The client says which protocol version it speaks and what *it* can offer: roots, because `client.py` passes a `list_roots` callback. The Python SDK numbers its requests from 0.

**Server → client · result for id 0**

```json
{
  "jsonrpc": "2.0", "id": 0,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "prompts":   { "listChanged": false },
      "resources": { "subscribe": false, "listChanged": false },
      "tools":     { "listChanged": false }
    },
    "serverInfo": { "name": "WeatherServer", "version": "1.30.0" }
  }
}
```

Same `id`, so the client knows which request this answers. The server agrees on the version and lists its features: prompts, resources and tools. (The version number is the MCP SDK's.)

**Client → server · `notifications/initialized` · notification**

```json
{ "jsonrpc": "2.0", "method": "notifications/initialized" }
```

No `id`: it's a notification, so no reply comes back. The handshake is complete and normal work can begin.

**Client → server · `tools/list` · request id 1**

```json
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }
```

Discovery: what tools do you have?

**Server → client · result for id 1 (shortened)**

```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": { "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city.",
      "inputSchema": {
        "type": "object",
        "properties": { "city": { "type": "string", "title": "City" } },
        "required": ["city"]
      },
      "outputSchema": { … }
    },
    { "name": "list_client_roots",
      "inputSchema": { "type": "object", "properties": {} }, … }
  ]}
}
```

FastMCP built the `inputSchema` from the Python signature `get_weather(city: str)` and the description from its docstring. Next, `client.py` sends `resources/list`, `resources/templates/list` and `prompts/list` (ids 2 to 4) the same way; they're skipped here.

**Client → server · `tools/call` · request id 5**

```json
{
  "jsonrpc": "2.0", "id": 5, "method": "tools/call",
  "params": { "name": "get_weather", "arguments": { "city": "London" } }
}
```

Run one tool with arguments. In an agent, the model chooses the tool and the arguments; here `client.py` hard-codes them.

**Server → client · result for id 5**

```json
{
  "jsonrpc": "2.0", "id": 5,
  "result": {
    "content": [ { "type": "text", "text": "Weather in London: 15°C, cloudy" } ],
    "structuredContent": { "result": "Weather in London: 15°C, cloudy" },
    "isError": false
  }
}
```

`content` is what a model reads; `structuredContent` matches the output schema for programs; `isError` says whether the tool failed. (Next, id 6 asks for Berlin and gets a polite "no data" answer.)

**Client → server · `resources/read` · request id 7**

```json
{
  "jsonrpc": "2.0", "id": 7, "method": "resources/read",
  "params": { "uri": "greeting://Developer" }
}
```

Read a resource by URI. `greeting://{name}` is a template; the client filled in `Developer`.

**Server → client · result for id 7**

```json
{
  "jsonrpc": "2.0", "id": 7,
  "result": { "contents": [ {
    "uri": "greeting://Developer",
    "mimeType": "text/plain",
    "text": "Hello, Developer! Welcome to the WeatherServer."
  } ] }
}
```

Read-only content with its MIME type. Nothing changed on the server. (Id 8 reads `courses://directory` the same way and gets JSON back.)

**Client → server · `prompts/get` · request id 9**

```json
{
  "jsonrpc": "2.0", "id": 9, "method": "prompts/get",
  "params": { "name": "weather_report", "arguments": { "city": "Tokyo" } }
}
```

Fill in a prompt template with arguments.

**Server → client · result for id 9**

```json
{
  "jsonrpc": "2.0", "id": 9,
  "result": {
    "description": "Generate a prompt asking for a weather report.",
    "messages": [ { "role": "user", "content": { "type": "text",
      "text": "Please provide a detailed weather report for Tokyo, including temperature, humidity, and forecast." } } ]
  }
}
```

Ready-made messages the host can send to its model. The server doesn't run a model itself. (Id 10 fills in `generate_study_plan` the same way.)

**Client → server · `tools/call` · request id 11**

```json
{
  "jsonrpc": "2.0", "id": 11, "method": "tools/call",
  "params": { "name": "list_client_roots", "arguments": {} }
}
```

The last call. To answer it, the server needs something only the client knows…

**Server → client · `roots/list` · server's request id 0**

```json
{ "jsonrpc": "2.0", "id": 0, "method": "roots/list" }
```

The protocol runs *backwards*: while request 11 is still open, the server sends its own request to the client. Each side numbers its own requests, so this one is the server's id 0.

**Client → server · result for the server's id 0**

```json
{
  "jsonrpc": "2.0", "id": 0,
  "result": { "roots": [
    { "uri": "file:///…/mcp-basics", "name": "Course workspace" }
  ] }
}
```

`client.py`'s `list_roots` callback answers with the course folder.

**Server → client · result for id 11**

```json
{
  "jsonrpc": "2.0", "id": 11,
  "result": {
    "content": [ { "type": "text",
      "text": "Course workspace: file:///…/mcp-basics" } ],
    "isError": false, …
  }
}
```

Now the tool can finish, using what the client told it.

**Shutdown · no JSON-RPC message**

The `async with` blocks in `client.py` end, the client closes the server's input stream, and the server process exits. (Over HTTP, the client closes the connection or ends the session.) MCP has no special "shutdown" method.

##### Securing the connection

MCP defines an **authorisation** framework for HTTP-based transports, built on **OAuth 2.1**. Servers reached over HTTP should follow it. Servers using stdio should *not*; they take any credentials they need from the environment instead, such as environment variables set when the client starts them. Clients and servers may also agree their own custom authentication and authorisation.
