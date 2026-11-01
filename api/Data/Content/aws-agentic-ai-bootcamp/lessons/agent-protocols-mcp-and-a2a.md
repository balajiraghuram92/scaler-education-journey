# Agent protocols: MCP and A2A

## 1.6 Agent protocols: MCP and A2A

Big agent systems run into a plumbing problem: every agent needs to talk to many tools, and often to other agents. Protocols are the shared plugs and sockets that make this manageable.

An agent often has to call external tools, APIs or databases to fetch information or take actions it can't do alone. A travel agent asked to book a flight may need a flight API, the customer's profile and a payment service. As tools and workflows multiply, teams need **one consistent way** to connect agents to external systems. That is the problem solved by the **Model Context Protocol (MCP)**, which standardises *agent-to-tool* communication.

Large systems also tend to use several specialised agents instead of one do-everything agent. A planner agent hands work to a booking agent, which in turn coordinates with a compliance or payment agent. Now the challenge is also *agent-to-agent* communication, which is what the **Agent-to-Agent (A2A) protocol** standardises.

Both exist so that agents and tools from different teams and vendors can work together without custom glue code for every pair. A **protocol** is just an agreed set of rules for that conversation.

{{diagram:1}}

*Why protocols exist. Without a standard, every agent needs custom code for every tool, and the count explodes as you grow. With one, each side is built once and works with everything else that speaks it.*

> **Think of it like this:**
> Remember the drawer full of different phone chargers? USB-C fixed it: one socket shape, any device. Or think of UPI: before it, each payment app needed a deal with each bank; now any UPI app works with any bank. MCP is that idea for agents and tools, and A2A is that idea for agents and other agents.

#### Model Context Protocol (MCP)

MCP gives agents a standard way to **discover and use tools** when there are many of them. Its promise is *write once, use anywhere*: build an MCP server for your database once, and any MCP-aware app or agent can use it.

MCP was introduced by Anthropic in late 2024 as an open protocol, and is now governed by the Agentic AI Foundation under the Linux Foundation. It provides a standard way to connect AI models to virtually any data source or tool. It uses a **client-server** design: you expose data and actions through lightweight **MCP servers**, and AI apps connect to them as **MCP clients**. Four parts make it work:

| Part | What it is | USB-C version |
| --- | --- | --- |
| Host | The program or AI tool that needs data through MCP: Claude Desktop, an IDE, or any AI application, including your own agent | Your laptop |
| Client | A protocol connector inside the host. Each client keeps a one-to-one connection with one server | One USB-C port |
| Server | A lightweight program that exposes capabilities through MCP and acts as a tool. It can offer tools (actions), resources (data to read) and prompts (reusable templates) | The device you plug in, like an external drive |
| Data sources | What a server connects to: local databases and file systems, or external systems over the internet through web APIs | The files on that drive |

{{diagram:2}}

*Host, clients, servers, data. The host owns the AI and the clients; each server is a separate small program that wraps one system. Add a new system by adding a server, without touching the agent's code.*

##### MCP in action: planning a warm January trip

Let's use the same travel agent, with a harder request: *"Book a 5-day trip to Europe in January. We like warm weather."* The host app (through its MCP clients) realises it needs outside data, connects through the protocol to specialised MCP servers for flights, hotels and weather, gets the data back, and gives the combined context to the LLM to produce a complete answer.

{{diagram:3}}

*The MCP workflow. Use the stepper below to light up one step at a time. Notice the host never talks to a database directly: it only ever speaks MCP to servers.*

Step through

##### Follow one request through MCP

Pick step 1 to begin.

On the wire

// messages appear here

1. 1 The request arrives The user's natural-language request is sent to the MCP host.
2. 2 The host works out what it needs Using an LLM, the host understands the request and identifies the data it needs: flights, hotels and weather.
3. 3 Clients call the servers The host uses the MCP protocol to ask the right MCP servers for exactly that data.
4. 4 Servers fetch from their sources Each server reads its own data source (a database, a file system or a web API) and returns the information to the host.
5. 5 The agent answers The AI agents inside the host process all this combined information and fulfil the original request.

**Each step of the stepper, with the messages on the wire:**

**1. The request arrives.** The user's message goes to the MCP host, the AI app that runs our agents.

```json
{
  "role": "user",
  "content": "Book a 5-day trip to Europe in January.\n              We like warm weather."
}
```

**2. The host works out what it needs.** It asks the LLM, which reasons: *warm in January means southern Europe or the Canary Islands; I need weather, then flights, then hotels.*

```
// the LLM plans these tool calls
[
  "get_climate(month=\"January\", region=\"Europe\")",
  "search_flights(origin=\"Bengaluru\", ...)",
  "find_hotels(city=..., nights=5)"
]
```

**3. Clients call the servers.** Each MCP client sends a standard `tools/call` request to its server. (When they first connected, each client asked its server which tools it offers, using `tools/list`.)

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "search_flights",
    "arguments": {
      "origin": "Bengaluru",
      "destination": "Tenerife",
      "date": "2027-01-12"
    }
  }
}
```

**4. Servers fetch from their sources.** The flights server queries its database, the hotels server reads its files, the weather server calls a web API. Each returns a result in the same MCP shape.

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [{
      "type": "text",
      "text": "BLR → MAD → TFE, 12 Jan, Rs 68,400"
    }]
  }
}
```

**5. The agent answers.** The host hands all results back to the LLM, which writes one complete plan for the user.

```
"Go to Tenerife in Spain's Canary Islands:
 around 21 °C in January. Fly on 12 Jan
 via Madrid; 5 nights at a beachfront
 hotel. Shall I book it?"
```

This is a *distributed* design: specialised MCP servers each handle access to one kind of data, and a central host, powered by an LLM for understanding and planning, coordinates them.

> **Running MCP on AWS:**
> MCP servers and clients can run on Amazon EKS or AWS Lambda, while the LLM is served by Amazon Bedrock or Amazon SageMaker AI inference. AWS also publishes an Amazon Bedrock AgentCore MCP server that helps you build agent components with built-in support for runtime, gateway integration, identity and memory. It suits rapid prototypes, production solutions, and scaling agent infrastructure across an enterprise.
>
> You will write your own MCP server and client in Section 5 (`section-05-mcp-and-a2a/mcp-basics`) and connect a Strands agent to MCP tools, then turn APIs into MCP tools with AgentCore Gateway in Section 6.

#### Agent-to-Agent protocol (A2A)

A2A is an open standard for agents to **discover each other and work together**. Google introduced it in 2025; it is now also hosted by the Agentic AI Foundation, alongside MCP. It gives agents a common language even when they were built with different frameworks by different companies.

**Why do we need it?** Imagine building a trip planner. You need a hotel agent, an activity agent, a flight agent and a local guide agent, all coordinating. Building every one yourself is a lot of work. You would rather reuse agents that others have already built, but you have no idea how they are implemented inside. A2A gives you a standard way to collaborate with them anyway.

{{diagram:4}}

*One orchestrator, many independent agents. The travel agent doesn't handle the details itself, and doesn't need to know how any of these agents work inside. It only needs them to speak A2A.*

Through A2A, the travel agent acts as the **orchestrator** for the whole trip. It delegates specific tasks to specialised agents without understanding their internal code. Each agent, whoever built it and however, communicates using standard A2A messages. This decentralised approach means you don't rebuild every component, and good specialised agents get reused.

> **Think of it like this:**
> A wedding planner doesn't cook, decorate or play music. They hire a caterer, a decorator and a DJ, agree on what's needed in a standard way (date, guests, budget, menu), and coordinate. They never need the caterer's recipes. A2A is that standard way of hiring and coordinating, for agents.

##### How A2A works

There are four players: the **user**, a **client agent** (Agent A, which acts for the user), and one or more **remote agents** (Agent B, the server, which does the work). The client agent sends tasks to remote agents over A2A and collects their results.

{{diagram:5}}

*Client and remote agents. The client agent works for the user and delegates. Remote agents publish an agent card describing what they can do, so the client knows whom to ask.*

Agents advertise their capabilities with an **Agent Card**, a small **JSON** document usually published at `/.well-known/agent-card.json`. The client agent reads cards to find the best agent for a task, then uses A2A to talk to it. Here is roughly what the card of the flights agent you build in Section 5 looks like:

```pseudo title="Agent card for a flights agent (illustrative)"
DEFINE the agent card as a JSON document:
    SET name = "Flights Agent"
    SET description = "Searches for and books flights between cities."
    SET url = the localhost address on port 9002
    SET version = "1.0.0"
    SET capabilities: streaming = on
    SET default input and output modes = text
    ADD one skill:
        id = "search_flights"
        name = "Search flights"
        description = "Find available flights between two cities."
        tags = travel, flights
        example request = "Find flights from London to Paris"
```

```json reveal title="Agent card for a flights agent (illustrative)"
{
  "name": "Flights Agent",
  "description": "Searches for and books flights between cities.",
  "url": "http://localhost:9002/",
  "version": "1.0.0",
  "capabilities": { "streaming": true },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "skills": [
    {
      "id": "search_flights",
      "name": "Search flights",
      "description": "Find available flights between two cities.",
      "tags": ["travel", "flights"],
      "examples": ["Find flights from London to Paris"]
    }
  ]
}
```

> **Think of it like this:**
> An agent card is a **visiting card plus a menu**: who I am, where to reach me, and the list of dishes I can make. The client agent reads the menus and orders from the right kitchen.

Try it

##### Let the client agent find the right remote agent

submitted working completed

Pick a task. The client agent will scan each card's skills.

**Task: "Find flights from Bengaluru to Lisbon on 12 January"**

Client agent is reading agent cards…

Match: the task is about **flights**, and the **Flights Agent** lists a `search_flights` skill. Sending the task over A2A…

**Flights Agent replied:** 2 options found. Cheapest: one stop via Dubai, Rs 71,200.

The client agent never saw how that agent works inside. It only read its card and spoke A2A.

**Task: "Find a 4-star hotel in Lisbon for 5 nights"**

Match: the task is about **hotels**, and the **Hotel Agent** lists a `find_hotels` skill. Sending the task over A2A…

**Hotel Agent replied:** 3 hotels found. Top pick: a riverside 4-star in Alfama, Rs 9,800 a night.

The client agent never saw how that agent works inside. It only read its card and spoke A2A.

**Task: "Is Lisbon warm in January?"**

Match: the task is about **weather**, and the **Weather Agent** lists a `get_climate` skill. Sending the task over A2A…

**Weather Agent replied:** Mild rather than warm: about 15 °C by day and 8 °C at night.

The client agent never saw how that agent works inside. It only read its card and spoke A2A.

> **MCP and A2A are partners, not rivals:**
> They solve different problems and are used together in the same system.

##### MCP vs A2A side by side

|  | Model Context Protocol (MCP) | Agent-to-Agent protocol (A2A) |
| --- | --- | --- |
| Main role | Connects an agent to tools, APIs and resources. Think: how an agent uses its capabilities (function calling) | Lets different agents communicate as peers. Think: how agents collaborate, delegate and manage tasks |
| Example | An agent uses MCP to call a weather API tool | A travel booking agent uses A2A to ask another agent to find flights |
| Relationship | Complementary, not competing | Complementary, not competing |

{{diagram:6}}

*Down to tools, across to peers. MCP goes "down" from an agent to the tools it uses. A2A goes "across" between agents. A remote agent can use MCP for its own tools, and you never see that from outside.*

> **Think of it like this:**
> At work, using your laptop, the CRM and the printer is MCP. Emailing a colleague in the finance team and asking them to process an invoice is A2A. You need both to get anything done.

> **Running A2A on AWS:**
> A2A is supported on Amazon Bedrock AgentCore Runtime, so agents deployed there can discover peers, share capabilities and coordinate across platforms. You'll build A2A travel agents in Section 5 (`section-05-mcp-and-a2a/a2a-travel-agents`) and run a multi-agent system on AgentCore in Section 6.
