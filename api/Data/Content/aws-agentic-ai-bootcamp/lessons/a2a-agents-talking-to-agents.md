# A2A: agents talking to agents

## 5.8 A2A: agents talking to agents

MCP connects an agent to tools. But what about connecting an agent to another *agent*, perhaps built by a different team, in a different framework, running somewhere else?

The **Agent-to-Agent (A2A) protocol** is a standard bridge that lets agents built on different stacks (LangGraph, CrewAI, Google ADK, Strands and others) communicate, discover each other and manage shared workflows, even across organisations. Google introduced it in 2025; it has since merged with IBM's Agent Communication Protocol (ACP) and is now a vendor-neutral project governed by the Linux Foundation.

A2A is about peer-to-peer collaboration between **opaque** agents: they can delegate complex tasks and solve open-ended problems while keeping their internals private. MCP, in contrast, connects agents to specific tools and functions.

#### MCP vs A2A: why not just wrap an agent as a tool?

MCP reduces the complexity of connecting agents to tools and data. Tools are usually **stateless** and do one predefined thing (a calculator, a database query). So could you simply expose an agent as an MCP tool? Sometimes, and Section 4 did something similar inside one program. But as a general approach for independent agents it's limiting: **tools execute actions; agents solve problems.** Squeezing an agent into a tool call hides what it can really do: handle ambiguity, ask follow-up questions, run multi-step and long-running work, report progress.

A2A complements MCP. It lets agents collaborate in their natural mode, talking as agents (or as users) rather than as function calls, which enables multi-turn interactions where agents reason, plan and delegate.

{{diagram:1}}

*A2A between agents, MCP inside each. The two agents collaborate as peers; each uses its own MCP-connected tools to do its part.*

1. 1 The patient's request goes to the diagnosis agent
2. 2 It talks to the insurance agent over A2A
3. 3 Each agent acts with its own MCP-connected tools The diagnosis agent reaches the hospital's **EMR/EHR** systems; the insurance agent reaches insurance and pharmacy APIs.
4. 4 Information flows back and forth over A2A until the task is complete

#### Why agents need a standard protocol

As agents become more capable they also become more specialised, and more likely to work inside a larger multi-agent system. But the ecosystem is fragmented across frameworks, vendors and styles. A2A gives them a common protocol to communicate and coordinate across organisational and technical boundaries, without sharing their internals.

{{diagram:2}}

*Six reasons for a shared agent protocol. Different frameworks, harder tasks, and organisational boundaries all point to the same need: one common way for agents to talk.*

| Reason | In detail |
| --- | --- |
| Solve framework fragmentation | Agent frameworks (LangGraph, CrewAI, Microsoft's framework and others) aren't compatible out of the box. A2A lets agents talk whatever model or language they use. |
| Enable complex collaboration | Tasks like planning a whole trip (flights, hotels, activities) need several specialised agents; A2A gives the structure and methods to coordinate them. |
| A common language (the HTTP analogy) | The web needed HTTP to move data between different systems; the agent world needs A2A as a universal bridge beyond siloed apps. |
| Cross-organisation workflows | Agents collaborate across teams and companies while staying opaque: no internal implementation or private code is exposed. |
| Preserve agent capabilities | Agents handle ambiguity, multi-step workflows, coordination and open-ended goals. Reducing them to one tool call loses that; A2A supports the richer interaction. |
| Vendor neutrality | Hosted by the Linux Foundation and governed by a technical steering committee, so no single company controls how agents interact. |

#### A2A by example: a product launch

A marketing manager asks an AI system: *"Create and execute a launch plan for our new eco-friendly smartphone in the European market."* That needs many specialities, so (just like the multi-agent patterns in Section 4) a **lead orchestrator agent** breaks it down and works with:

{{diagram:3}}

*One request, four experts, four silos. Each agent is built differently, uses different data formats and runs on different systems, so without a shared protocol they can't even discover each other.*

Each specialist sits on its own system: market research on proprietary data, supply chain on the company's **ERP system**, creative content on an AI creative tool, legal on a secure legal model. Without A2A, each agent has its own bespoke development and deployment, so they can't collaborate, let alone discover what each other can do. A2A acts as the common communication layer: the orchestrator can **discover** agents by capability, agents **exchange information** in a shared format, and one agent can even **verify or approve** another's output. The orchestrator then combines everything into one launch playbook, turning weeks of human coordination into a fast, automated workflow.

> **Swarm vs A2A:**
> The swarm pattern from Section 4 organises agents *inside one multi-agent system*. A2A solves a different problem: standard communication between *independently built* agents, across frameworks, platforms and organisations. You could even run a swarm whose members talk A2A.

## 5.9 How A2A works

The protocol standardises only the bridge between agents. Agent A doesn't need Agent B's code, prompts or database; it only needs to format an A2A request and read an A2A response.

{{diagram:4}}

*Client agent, remote agent, business card. Agent A reads Agent B's card to learn where and how to talk to it, then sends a request.*

##### Agent A: the client agent

Starts the conversation and asks for work. Usually the front-facing agent that talks to the end user. It discovers other agents by reading their **agent cards** to see what they can do.

##### Agent B: the remote (server) agent

Receives the request and does the work. It hosts its capabilities at a URL and publishes its agent card at `/.well-known/agent-card.json`. It decides how to fulfil a request: a simple one gets a message straight back; a complex one becomes a **task** it manages until it produces an **artifact** (the result).

Here's a simplified agent card for a weather agent (you'll see a complete one from the lab in 5.11):

```pseudo title="an agent card"
SET agent card for "Weather Agent":
    capabilities: streaming = true, pushNotifications = false   // how it communicates
    skills: one skill with id "get_weather", name "Get Weather", and a description   // what work it can do
    url = "https://api.example.com/weather-agent/"   // where requests are sent
```

```json reveal title="an agent card"
{
  "name": "Weather Agent",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "get_weather",
      "name": "Get Weather",
      "description": "Returns current weather conditions for a given city."
    }
  ],
  "url": "https://api.example.com/weather-agent/"
}
```

> **Capabilities:**
> *How* this agent communicates: does it support streaming, push notifications…

> **Skills:**
> *What work* it can do: each skill has an id, name and description (and often tags and examples).

> **Opaque by design:**
> A remote agent never has to show how it works inside: which code, which model. It only has to produce the output the protocol defines.

#### Discovery and protocol bindings

Agents find each other through agent cards: JSON files at a well-known URL, a bit like an **OpenAPI (Swagger) document**, acting as a digital business card. A card details the agent's name, capabilities, supported protocols, media types and authentication requirements, including its **URI** (endpoint) and its supported **protocol bindings**.

A binding tells the client agent exactly which technical format to use with that remote agent. A2A provides the language; the binding is the physical connection that carries it.

> **Think of it like this:**
> You've written a letter in English (the common language, A2A). How do you send it? **HTTP binding** is ordinary post: the most common and easiest. **gRPC binding** is a high-speed courier: faster and more efficient for heavy data. **JSON-RPC binding** is a telegram: it follows a strict set of remote-control rules.

| Binding | In practice |
| --- | --- |
| JSON-RPC | JSON-RPC 2.0 over HTTP, with server-sent events for streaming. The binding this section's lab uses. |
| gRPC | Binary, high-performance remote calls (**gRPC**); good for heavy traffic |
| HTTP + JSON (REST) | Plain HTTP endpoints with JSON bodies |

> **Both sides must share a binding:**
> If one agent only speaks gRPC and the other only HTTP+JSON (REST), they can't talk directly. They must agree on a binding, which is exactly what their agent cards declare.

#### The A2A data model: messages, tasks, artifacts

{{diagram:5}}

*In: a message made of parts. Out: artifacts made of parts. In between, a task tracks the work and its status.*

1. 1 Message The client sends a **message** (one turn of interaction) made of one or more **parts**: text, JSON data, files.
2. 2 Task When the remote agent starts working, it may create a **task** to track progress over time, with an ID and a status.
3. 3 Artifacts As the task progresses or completes it produces **artifacts**, output containers that also hold parts.
4. 4 GetTask The client can call `GetTask` at any time to retrieve the latest status and whatever artifacts exist so far.

#### Communication styles

Tasks differ: some finish in a second, some take hours. A2A supports four ways of exchanging them:

{{diagram:6}}

*Four execution modes. From "wait right here" to "call me when it's done".*

##### Synchronous

For simple, immediate answers. Agent A sends a message with `SendMessage`; Agent B processes it and replies right away. The client waits for the result, so it suits quick, short-lived tasks.

##### Asynchronous (polling)

For complex or long-running jobs where the client shouldn't block. Agent B replies with a **task object** instead of the final result: a task ID plus a status. Agent A carries on and periodically calls `GetTask` with that ID. When the task reaches a completed state, the results come back as artifacts.

In the Python A2A SDK, a plain `message/send` waits for the answer by default. To poll instead, the client sets `ClientConfig(polling=True)`; the request then asks the server not to block, and the client calls `GetTask` (`tasks/get`) in a loop until the task is finished.

{{diagram:7}}

*Take a token, check back later. Agent A isn't stuck waiting; it polls with the task ID until the status reaches a final state.*

##### Streaming

Uses server-sent events to deliver real-time updates or text in chunks as it's generated, so you see live progress. It's only available if the server sets `capabilities.streaming = true` in its agent card. Agent A calls `SendStreamingMessage`; the server keeps an HTTP connection open (`text/event-stream`) and sends structured events (status changes, intermediate messages, partial results) until the task completes.

{{diagram:8}}

*Updates as they happen. One open connection carries a stream of events, so the client sees progress without asking.*

##### Push notifications

For tasks that take a long time, or when the client can't stay connected. Instead of polling or streaming, the client gives a **webhook** URL and the server calls it when something important happens, such as completion or "input required". A pharmacy agent might notify a healthcare system hours later when a prescription is ready; a flights agent might notify when a booking is confirmed. Ideal for long-running, event-driven work.

{{diagram:9}}

*"Don't call us, we'll call you." No open connection, no polling: the server rings the client's doorbell when it matters.*

Push notifications only work if the server declares `capabilities.pushNotifications = true` in its agent card. Agent A supplies a `PushNotificationConfig` (webhook URL plus optional authentication) with the first request or through a separate call. Agent B then POSTs to that webhook on significant updates, and Agent A usually follows up with `GetTask` to fetch the full task and results.

> **Method names on the wire:**
> The A2A spec names its operations `SendMessage`, `SendStreamingMessage` and `GetTask`. With the JSON-RPC binding and the `a2a-sdk` 0.3 used in this section, they travel as the methods `message/send`, `message/stream` and `tasks/get`.

Try it

##### Four ways to ask the flights agent to book a ticket

**Synchronous**

- **Agent A:** `SendMessage` “Book flight AE303 for Asha Rao”. The connection stays open while it waits.
- **Agent A:** Waiting… can't do anything else with this request until the reply arrives.
- **Agent B:** Checks the flight, reserves a seat, issues the booking.
- **Agent B:** Reply on the same connection: task **completed**, artifact “Booking confirmed: AE303, Asha Rao”.

**Synchronous:** one request, one response. The simplest style, but Agent A is blocked until B finishes. Best for quick jobs.

**Asynchronous (polling)**

- **Agent A:** `SendMessage` “Book flight AE303 for Asha Rao”.
- **Agent B:** Returns at once: `Task {id: 12345, status: submitted}`.
- **Agent A:** Free to do other work. Checks back later.
- **Agent A:** `GetTask 12345` → **working**
- **Agent A:** `GetTask 12345` → **input-required**: “Window or aisle seat?”
- **Agent A:** Sends a follow-up message on the same task: “Aisle, please.”
- **Agent A:** `GetTask 12345` → **working**
- **Agent A:** `GetTask 12345` → **completed**, artifact “Booking confirmed: AE303, seat 14C”.

**Asynchronous polling:** B hands back a task ID immediately and A checks its status with `GetTask`. The task can pause in **input-required** until A answers. Good for longer jobs when A can't hold a connection open.

**Streaming**

- **Agent A:** Card says `capabilities.streaming: true`, so it sends `SendStreamingMessage` “Book flight AE303 for Asha Rao”.
- **Agent B:** event: status = **working**
- **Agent B:** event: “Checking seat availability on AE303…”
- **Agent B:** event: “Seat 14C held, issuing ticket…”
- **Agent B:** event: artifact update “Booking confirmed: AE303, seat 14C”
- **Agent B:** event: status = **completed**. The stream closes.

**Streaming:** one long-lived connection carrying server-sent events. A sees progress and partial results live. Good when a human is watching.

**Push notification**

- **Agent A:** Card says `capabilities.pushNotifications: true`, so it sends `SendMessage` “Book flight AE303 for Asha Rao” with a `PushNotificationConfig`: webhook URL plus a token.
- **Agent B:** Returns: `Task {id: 12345, status: submitted}`.
- **Agent A:** Disconnects. No open connection, no polling. Hours can pass.
- **Agent B:** The airline confirms. Agent B POSTs to Agent A's webhook: “task 12345 completed”.
- **Agent A:** Verifies the token, then calls `GetTask 12345` for the full result.
- **Agent A:** Task **completed**, artifact “Booking confirmed: AE303, seat 14C”.

**Push notifications:** B calls A's webhook when something important happens. Best for long-running, event-driven work where staying connected or polling is wasteful.
