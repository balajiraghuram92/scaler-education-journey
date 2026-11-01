# Glossary

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 4. Course code is provided under the MIT License.

AWS service names, tool names and library versions change often. When something here differs from what you see, the current documentation wins.

- **Context rot** — The drop in accuracy when a model's context is stuffed with too much or irrelevant material: it loses focus, misses details and makes mistakes.
- **Multi-agent pattern** — A reusable way of organising several AI agents to work towards one goal: who talks to whom, who decides the order, and how results are combined.
- **Supervisor–worker** — A pattern where one coordinating agent delegates subtasks to specialist worker agents and combines their results. Workers only talk to the supervisor.
- **Concurrently** — At the same time. Strands runs the tool calls a model requests in one turn concurrently by default, so independent workers don't wait for each other.
- **Bottleneck** — The narrowest point in a system, where work queues up because everything must pass through it.
- **Single point of failure** — One component whose failure stops the whole system.
- **Horizontal scaling** — Handling more load by running more copies of a component side by side, rather than making one copy bigger.
- **Prompt caching** — Reusing the processed form of a long, repeated prompt prefix (such as a big system prompt) so later calls are faster and cheaper.
- **Failover** — Automatically switching to a standby copy when the main one fails.
- **Agent as tool** — Wrapping an agent so other agents can call it like a normal tool. Its name and description tell callers when to use it.
- **Orchestrator** — The agent (or code) that decides which other agents or tools to call, in what order, and combines the results.
- **Sequential communication** — Agents work one after another; each passes its output to the next. Total time is the sum of the steps.
- **Parallel communication** — Several agents work at the same time on independent parts of a problem; results are combined at the end. Total time is the slowest step.
- **Collaborative communication** — Agents talk back and forth, critique each other and negotiate until a solution satisfies all their constraints.
- **Rate limit** — A cap on how many requests (or tokens) you may send to an API per minute. Going over it gets your calls throttled.
- **Swarm** — A pattern with no central coordinator: agents hand control to each other through handoffs, sharing one context, until one finishes without handing off.
- **Handoff** — One agent explicitly passing control of the task to another agent, with a message about what it needs.
- **Blockout** — In game design, a rough 3D draft of a level built from simple shapes, used to test layout before any detailed art.
- **Ping-pong (in a swarm)** — Two agents passing the same task back and forth without making progress. Strands detects it by counting unique agents in recent turns.
- **Graph pattern** — A pattern where you define, in code, the nodes (steps) and edges (allowed paths with conditions) that work must follow.
- **Directed graph** — A set of nodes connected by arrows that point one way, from one node to the next.
- **DAG (directed acyclic graph)** — A directed graph with no loops: arrows only point forward, so every run is guaranteed to reach an end.
- **Edge condition** — A small function attached to a graph edge that returns True or False. The edge is followed only when it returns True.
- **Regular expression (regex)** — A compact pattern language for finding text, such as "the word after RISK_CATEGORY:".
