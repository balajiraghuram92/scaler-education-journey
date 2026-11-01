# Recap and self-check

## 5.12 Recap and self-check

Your agents can now plug into any tool that speaks MCP, and talk to any agent that speaks A2A.

Standard protocols make agentic systems easier to build, extend and scale. You started with **MCP**, which solves the explosion of custom integrations between many AI apps and many tools: instead of N × M connectors, everything speaks one shared interface through **hosts, clients and servers**. You saw how messages travel (JSON-RPC over stdio or Streamable HTTP), how a connection is set up and closed (the lifecycle), how remote servers are protected (authorization), and what servers offer: **tools** to act, **resources** to read and **prompt templates** to ask consistently. Clients can offer things back: **sampling**, **roots** and **elicitation**.

Then you met **A2A**, which solves a different problem: letting agents, open-ended problem solvers rather than simple tools, collaborate without exposing their insides. Agents discover each other through **agent cards**, exchange **messages**, track work as **tasks** and return **artifacts**, in four interaction styles: synchronous, asynchronous polling, streaming and push notifications.

In the labs you built an MCP weather server with FastMCP, called it from a raw client and from Strands agents, and then ran a travel orchestrator that talks to weather and flights agents over A2A. The two protocols **complement** each other: A2A for collaboration between agents, MCP for each agent's own work with tools and data.

{{diagram:1}}

*Two protocols, two layers. Built in this section with FastMCP and the MCP client on one side, and Strands `A2AServer` plus the A2A SDK on the other.*

Try it

##### MCP or A2A?

For each situation, pick the protocol that fits best.

0 of 6 answered

**1. Give a coding assistant access to your GitHub issues and pull requests.**

**Answer: MCP.** An LLM app reaching a tool and its data: that's MCP. A GitHub MCP server gives any MCP host the same access.

**2. A hospital's scheduling agent asks an insurance company's agent to verify a patient's coverage.**

**Answer: A2A.** Two independent agents owned by different organisations, collaborating without sharing their insides: that's A2A.

**3. Let a chat app read your team's database schema as context.**

**Answer: MCP.** Read-only context for a model is an MCP resource.

**4. Your travel orchestrator delegates weather questions to another team's weather agent, without knowing how it works inside.**

**Answer: A2A.** Delegating to an opaque agent, discovered through its agent card: that's A2A, exactly as in the lab.

**5. Share a “summarise this meeting” instruction template that every AI app in your company can reuse.**

**Answer: MCP.** A reusable prompt template offered by a server: that's MCP.

**6. A booking agent that takes hours to confirm must tell the requesting agent when it's done.**

**Answer: A2A.** Agent-to-agent, long-running and event-driven: A2A push notifications to a webhook.

MCP connects agents to tools and data; A2A connects agents to agents.

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| Why MCP | N apps × M tools custom integrations become N + M implementations of one standard |
| Host, client, server | The app the user sees; one connector per server inside it; the program that offers capabilities |
| Transports | stdio for local child processes, Streamable HTTP for remote servers, custom (e.g. gRPC) when needed |
| Lifecycle | `initialize` → result → `notifications/initialized` → normal work → close the connection |
| Tools, resources, prompts | Do things; read things without side effects; reuse good instructions |
| Sampling, roots, elicitation | Server borrows the client's model; client limits where the server may work; server asks the user for missing details |
| FastMCP | Decorators (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`) turn Python functions into MCP features |
| Strands + MCP | `MCPClient` starts or connects to a server; `list_tools_sync()` hands its tools to an `Agent` |
| Why A2A | Agents are opaque, open-ended problem solvers; they need a standard way to discover and delegate to each other |
| Agent card | A JSON document at `/.well-known/agent-card.json`: name, skills, capabilities, endpoint |
| Message, task, artifact | The request; the unit of work with an ID and status; the output |
| Four styles | Synchronous, polling with `GetTask`, streaming over SSE, push to a webhook |
| `A2AServer` | Wraps a Strands agent as an A2A HTTP server that publishes its own card |

#### When something goes wrong

| What you see | What it usually means and how to fix it |
| --- | --- |
| Import errors or unexpected API errors from `mcp` | A different major version of the MCP SDK is installed. Run `pip install -r requirements.txt` in the lab folder; it pins `mcp` below 2.0. |
| `` `uvx` not found. Install uv first `` | The AWS documentation lab launches its server with `uvx`. Install the folder's requirements (they include `uv`) or run `pip install uv`. |
| The AWS docs agent is slow or times out the first time | `uvx` downloads the server package on first run. The script already allows 120 seconds; run it again once the download has finished. |
| `AccessDeniedException` or credential errors from Bedrock | Your AWS credentials can't call the model. Check `AWS_REGION`, your credentials, and that `BEDROCK_MODEL_ID` is available to your account. |
| `address already in use` when starting an A2A server | An earlier copy is still running on port 9001 or 9002. Stop it with Ctrl+C in its terminal (or close that terminal), then start again. |
| The orchestrator fails with a connection error | It can't reach an agent. Start both servers first (terminals 1 and 2) and wait until each shows `Uvicorn running on …` before running the orchestrator. |
| `No response received.` | The server answered without any artifacts, usually because its agent hit an error. Look at that server's terminal for the real message (often a Bedrock error). |
| "No flights found" or "No weather data available" | The city or route isn't in the lab's fake data. Use one from the Available data table; the agent lists what it has. |

> **Nothing to clean up:**
> Everything in this section runs on your own machine and only calls Bedrock (plus the public AWS documentation site in one lab). No AWS resources are created, so there's nothing to delete. Stop the A2A servers with Ctrl+C when you're done.

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

Score: 0 of 10 answered

**1. What problem does MCP mainly solve?**

- Models being too slow
- Every AI app needing its own custom integration with every tool (N × M)
- Agents forgetting earlier conversations
- Agents sharing GPUs

**Answer: Every AI app needing its own custom integration with every tool (N × M).** MCP replaces N × M custom integrations with N + M implementations of one standard: one client per app, one server per tool.

**2. How many MCP servers does a single MCP client talk to?**

- Exactly one
- Up to three
- As many as the host has
- None; servers talk to hosts

**Answer: Exactly one.** Each client keeps a one-to-one connection with one server. A host that uses five servers creates five clients.

**3. Your client starts the server as a child process on the same machine. Which transport is that?**

- Streamable HTTP
- gRPC
- stdio
- A webhook

**Answer: stdio.** With stdio, the client launches the server and they exchange JSON-RPC messages through standard input and output, as in mcp-basics/client.py.

**4. Which message completes the MCP initialization handshake?**

- tools/list
- notifications/initialized
- resources/read
- shutdown

**Answer: notifications/initialized.** After the initialize request and its result, the client sends notifications/initialized. It has no id, so no reply comes back.

**5. A server wants to share a read-only student directory that the model can look things up in, with no side effects. Which feature fits?**

- A tool
- A prompt template
- A resource
- Elicitation

**Answer: A resource.** Resources are read-only data addressed by a URI. Reading one changes nothing.

**6. A server has the data but no AI model. It wants an AI to rank activities, with the user approving. Which client feature allows that?**

- Sampling
- Roots
- Elicitation
- Authorization

**Answer: Sampling.** Sampling lets the server ask the client's model to do an AI task, with the user able to review and approve.

**7. Where does an A2A client look first to learn what a remote agent can do?**

- Its source code
- Its system prompt
- The agent card at /.well-known/agent-card.json
- The model's documentation

**Answer: The agent card at /.well-known/agent-card.json.** The agent card lists the agent's name, skills, capabilities and endpoint. Clients fetch it before sending any message.

**8. A remote agent returns a task with status input-required. What does that mean?**

- The task failed
- The agent needs more information from the client before it can continue
- The client must restart the agent
- The task was rejected

**Answer: The agent needs more information from the client before it can continue.** input-required pauses the task until the client sends a follow-up message with the missing detail, like choosing a seat.

**9. In the lab, how does travel_orchestrator.py decide whether to use streaming?**

- It always streams
- A command-line flag
- It reads capabilities.streaming from the agent card
- It asks the LLM

**Answer: It reads capabilities.streaming from the agent card.** use_streaming = bool(card.capabilities and card.capabilities.streaming). Strands' A2AServer always advertises streaming in the card, so the lab streams; enable_a2a_compliant_streaming only chooses the event format.

**10. Which sentence best describes how MCP and A2A relate?**

- A2A replaces MCP
- They are two names for the same protocol
- MCP is for agents, A2A is for tools
- A2A connects agents to agents; MCP connects each agent to its tools and data

**Answer: A2A connects agents to agents; MCP connects each agent to its tools and data.** They work at different layers and complement each other, as in the A2A-outside, MCP-inside design.

**If you score 8 or more:** Great work, you're ready for Section 6.

**If you score fewer than 8:** Revisit the parts you missed, then try Section 6.

> **Up next: Section 6, shipping agents to production:**
> Everything so far has run on your laptop. Next you'll deploy agents on AWS: Amazon Bedrock AgentCore Runtime, Amazon ECS on Fargate and AWS Lambda, plus AgentCore Gateway, which turns an existing REST API into MCP tools. The final lab puts this section's ideas in the cloud: an orchestrator calls a stock agent over A2A, and that agent gets its tools over MCP. Folder: `section-06-production-deployment`.

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 5. Course code is provided under the MIT License.

AWS service names, tool names, protocol versions and library versions change often. When something here differs from what you see, the current documentation wins.

- **MCP (Model Context Protocol)** — An open standard for connecting AI applications to tools, data and prompt templates. Build a connector once as an MCP server and any MCP-compatible app can use it.
- **MCP host** — The AI application the user actually works in, such as a chat app, an IDE or your own agent. It contains one MCP client for each server it connects to.
- **MCP client** — The connector inside a host that talks to exactly one MCP server: it opens the connection, discovers what the server offers and passes requests and results back and forth.
- **MCP server** — A program that offers tools, resources and prompt templates to MCP clients. It can run on your machine (started as a child process) or remotely over HTTP.
- **Transport** — How MCP messages physically travel between client and server: through standard input/output pipes (stdio), over HTTP, or a custom channel. The messages themselves are the same.
- **JSON-RPC 2.0** — A simple standard for remote calls written in JSON. A request names a method and its parameters and carries an ID; the response carries the same ID with a result or an error. Notifications have no ID and expect no reply.
- **stdio (standard input/output)** — The text pipes every program has for input and output. With the stdio transport, the client starts the server as a child process and they write JSON-RPC messages to each other through these pipes.
- **SSE (server-sent events)** — A way for a server to keep an HTTP response open and push a stream of small events to the client as they happen, instead of one reply at the end.
- **Lifecycle** — The fixed order of an MCP connection: initialize (agree on versions and capabilities), normal operation, then shutdown.
- **Authorization** — Checking that a caller is allowed to use a server. Remote MCP servers over HTTP can use OAuth 2.1 access tokens; local stdio servers take credentials from their environment instead.
- **Tool (in MCP)** — A function an MCP server exposes for the model to call, such as searching, sending a message or updating a record. Clients find them with tools/list and run them with tools/call.
- **Resource** — Read-only data an MCP server exposes, such as a file, a database record or an API response. Reading a resource gives context without changing anything.
- **URI** — A unique address for a piece of data, written like file:///docs/notes.md or greeting://Asha. MCP uses URIs to name resources.
- **MIME type** — A standard label for what kind of content something is, such as text/plain, application/json or application/pdf, so the receiver knows how to handle it.
- **Resource template** — A pattern for a family of resources with a placeholder, such as greeting://{name}. The client fills in the placeholder to read a specific one.
- **Prompt template** — A reusable, predefined prompt that an MCP server offers, with arguments to fill in, such as a weather report for a given city. Users usually pick them explicitly.
- **Sampling** — An MCP client feature that lets a server ask the client's model to generate text for it, with the user able to review and approve. The server needs no model of its own.
- **Roots** — Folders or URIs the client tells a server it may work within. They scope what the server should touch, and the client can update them when the user switches projects.
- **Elicitation** — An MCP client feature that lets a server ask the user for missing information in the middle of a task, either through a structured form or by sending them to a URL.
- **FastMCP** — The high-level part of the Python MCP SDK. Decorators like @mcp.tool(), @mcp.resource() and @mcp.prompt() turn ordinary Python functions into MCP features.
- **FastAPI** — A popular Python framework for building web APIs for any client. Its design inspired FastMCP, but it speaks plain HTTP, not MCP.
- **uvx** — A command that comes with the uv package manager. It downloads a Python tool into a temporary environment and runs it in one step, which is handy for starting MCP servers.
- **A2A (Agent2Agent protocol)** — An open standard that lets independent AI agents, built by different teams on different frameworks, discover each other and work together over HTTP.
- **Opaque agent** — An agent that collaborates without revealing its internals: other agents see only its card, its messages and its results, never its memory, tools or prompts.
- **Agent card** — A JSON document an A2A agent publishes, usually at /.well-known/agent-card.json, describing its name, skills, capabilities, endpoint and how to authenticate. Clients read it before sending anything.
- **Agent skill** — One entry in an agent card describing something the agent can do: an ID, a name, a description, tags and example requests. In Python it's an AgentSkill object.
- **Protocol binding** — The concrete format A2A messages travel in: JSON-RPC, gRPC or plain HTTP+JSON. The meaning is the same; only the wrapping differs.
- **Message (A2A)** — One turn of communication between agents, with a role (user or agent) and one or more parts: text, files or structured data.
- **Task (A2A)** — The unit of work a remote agent creates to track a request, with an ID and a status such as submitted, working, input-required or completed.
- **Artifact** — An output a remote agent produces for a task, such as a report, a booking confirmation or a file, made up of parts.
- **Webhook** — A URL you give to another system so it can call you when something happens. It's how A2A push notifications reach the client.
- **OAuth 2.1** — The standard way for an app to get a limited, expiring access token to act on a user's behalf, instead of handling their password. MCP uses it to protect remote servers.
- **gRPC** — A fast way for programs to call each other over the network, using compact binary messages instead of JSON text. Popular for high-traffic internal services.
- **OpenAPI (Swagger)** — A standard JSON or YAML document that describes a web API: its endpoints, inputs and outputs. Tools can read it to learn how to call the API.
- **Stateless** — Keeps no memory between calls: the same input always gets handled the same way, with nothing remembered from earlier requests.
- **EMR / EHR** — Electronic medical record / electronic health record: the hospital systems that store patients' histories, diagnoses and treatments.
- **ERP system** — Enterprise resource planning: a company's central software for inventory, orders, shipping, finance and other operations.
- **uvicorn** — A fast Python web server that runs async web apps. A2AServer.serve() uses it to listen for HTTP requests.
