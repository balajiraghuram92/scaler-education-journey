# When multi-agent is not the answer

## 4.8 When multi-agent is not the answer

You now know supervisor–worker, swarms and graphs. Here's what doesn't get said often enough: most problems don't need multiple agents.

It's a common story. Someone learns about multi-agent systems and immediately rebuilds a working single-agent app as five agents coordinating through a graph. The demo looks impressive. Then it goes live.

Debugging becomes a nightmare. Which agent failed? Was it agent three's input or agent two's output? The logs show five execution paths and you're tracing which one ran. The single agent used to answer in 3 seconds; the multi-agent version takes 12 because of coordination overhead. And the error rate went *up*, because there are now five points of failure instead of one.

{{diagram:1}}

*Complexity has a price. Coordination overhead, more ways to fail, and much harder debugging. Pay it only when you get something real in return.*

> **Think of it like this:**
> You don't hire a committee to fix a leaking tap. A good plumber with the right toolkit is faster, cheaper and easier to hold accountable. You call in a team for building a house, not for every job.

**A single agent with good tools beats a poorly designed multi-agent system.** Before you design something complex, try giving one agent the right tools. Can it call your APIs? Query your databases? Run code? Read your documentation? If you structure the tools well, most problems fit in one agent's context window.

The patterns in this section solve real problems, but they aren't default architectures. You'll know you need multiple agents when you hit actual limits:

1. 1 The context window keeps filling up You're processing thousands of documents and the agent loses track.
2. 2 You need true parallelism Waiting for three sequential 30-second API calls is too slow for your users.
3. 3 The expertise genuinely doesn't fit in one prompt The roles need such different instructions and tools that one prompt becomes a muddle.

> **The rule of thumb:**
> Start with one agent, give it tools, and test it. Only add agents when one agent clearly can't cope. Three agents that work reliably beat ten that don't.

Try it

##### Do you need a team? Which one?

Answer the questions above.

**1. Can one agent with good tools already do the job well?** Yes / No / Haven't tried yet

**2. Do parts of the work need genuinely different expertise, prompts or tools?** Yes / No

**3. Must certain steps always happen in a fixed, auditable order?** Yes / No

**4. Can you predict the path the work will take?** Yes / No

**5. Do you need one combined answer from several independent specialists?** Yes / No

- **Suggestion: One agent.** Keep it simple. One agent with good tools is faster, cheaper and easier to debug. (Question 1: Yes)
- **Suggestion: Try one agent first.** Give one agent the right tools and test it. Add agents only when you hit a real limit. (Question 1: Haven't tried yet)
- **Suggestion: Still one agent.** If the expertise isn't really different, fix the single agent instead: better tools, a clearer prompt, or context management (Section 3). (Questions 1 and 2: No)
- **Suggestion: Graph.** Routing lives in code, so every order of steps is guaranteed and auditable. (Question 1: No, question 2: Yes, question 3: Yes)
- **Suggestion: Swarm.** Agents hand work to each other as issues appear. Set handoff limits and ping-pong detection. (Question 1: No, question 2: Yes, question 3: No, question 4: No)
- **Suggestion: Supervisor–worker.** Fan out to specialists in parallel, then synthesise one answer. (Question 4: Yes, question 5: Yes)
- **Suggestion: Agent as tool.** Reusable specialists that an orchestrator calls when needed, while it stays in control. (Question 5: No)

## 4.9 Recap and self-check

You can now build teams of agents, and, just as importantly, decide when not to.

You started with the basic question of when several agents beat one. You built a supervisor that fans questions out to news, financial and sentiment workers and synthesises one answer, and a teacher that reuses specialist tutors as tools. You followed data through a multi-agent system and learned the three ways agents communicate: **sequential** for dependencies, **parallel** for speed (and voting for accuracy), and **collaborative** for negotiating trade-offs. Then you organised whole systems: a **swarm** that hands work around when the path can't be predicted, and a **graph** with explicit, auditable routes. Most production systems combine these patterns; the skill is matching the pattern to your constraints.

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| Signs you need a team | Context overload, mediocre results everywhere, no parallelism, hard to debug |
| Four aspects | Orchestration, specialisation, collaboration, coordination |
| Supervisor–worker | A coordinator fans out to specialists, who never talk to each other, then synthesises one answer |
| `agent.as_tool()` | Turns an agent into a tool; its name and description tell the caller when to use it |
| Agent as tool | Build a specialist once, reuse it anywhere; the orchestrator stays in control |
| Sequential / parallel / collaborative | Sum of times / slowest time / several rounds of calls |
| Voting | Independent agents outvote each other's mistakes; correlated agents don't |
| Swarm | Agents hand off with `handoff_to_agent`, share context, and stop when nobody hands off; limits prevent loops |
| Graph | Nodes, edges with conditions, dependencies; routing lives in code, so it's auditable |
| When not to | One agent with good tools first; add agents only at a real limit |

#### When something goes wrong

| What you see | What it usually means and how to fix it |
| --- | --- |
| "TAVILY_API_KEY not set", or the news agent says it can't search | Export the key before starting Jupyter, or set it in the commented lines of the keys cell, then re-run the cells that create the agents. |
| Financial numbers show "N/A" | Yahoo Finance left that field empty for this ticker. `_num` handles it; the agent works with what's available. |
| `ThrottlingException` from Bedrock | Parallel workers and swarms make many calls quickly. Wait and retry, run fewer questions at once, or ask for a higher quota. |
| The teacher answers the question itself | Its prompt says "Never solve problems yourself". Check the prompt ran unchanged and the tutors are in `tools=[...]`. |
| A graph run stops after `risk_analysis` | No condition matched: the risk analyser didn't end with a valid `RISK_CATEGORY:` line. Print `result.results["risk_analysis"].result` to see what it wrote. |
| The swarm stops early (`Status.FAILED`) with a repetitive-handoff, max-handoffs or timeout reason | The safety limits did their job. Make the prompts clearer about who to hand off to and when to finish, or raise the limits slightly. |
| The swarm takes several minutes | Normal: 10 or more full agent turns. Each costs model calls, so don't run it in a loop. |

> **Nothing to clean up:**
> These notebooks only call Bedrock (and the Tavily and Yahoo Finance APIs). They create no AWS resources, so there's nothing to delete. The cost is model usage, which is highest for the swarm.

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

**1. Which is NOT one of the warning signs that one agent is carrying too much?**

- Context overload
- Mediocre results across many tasks
- It answers in under a second
- Hard to tell which part failed

> **Answer:** It answers in under a second. Speed isn't a warning sign. Context overload, jack-of-all-trades results, no parallelism and hard debugging are.

**2. Three parallel workers each returned a correct answer, but the investor still asked “So, should I invest?” What was missing?**

- More workers
- A supervisor to synthesise one recommendation
- A faster model
- Sequential execution

> **Answer:** A supervisor to synthesise one recommendation. The workers did their jobs; nobody combined their findings. That's the supervisor's job.

**3. In supervisor–worker, how does the sentiment agent share a finding with the financial agent?**

- Through the supervisor
- It calls the financial agent directly
- Through a shared database
- It can't share anything

> **Answer:** Through the supervisor. Workers never talk to each other; all communication goes through the supervisor. That's also one of the pattern's trade-offs.

**4. What do an agent's name and description become when you use it as a tool?**

- Its system prompt
- Log labels only
- Nothing; they're ignored
- The tool name and the tool description the caller reads

> **Answer:** The tool name and the tool description the caller reads. The caller picks tools by reading names and descriptions, so a clear description is how the teacher knows when to call math_tutor.

**5. You want to add a history tutor to the teacher. What do you change?**

- Rewrite the routing if-statements
- Retrain the model
- Create a history_tutor agent and add it to the teacher's tools
- Change every other tutor's prompt

> **Answer:** Create a history_tutor agent and add it to the teacher's tools. No routing code exists. The teacher discovers the new tool from its description.

**6. Agents take 10, 15 and 5 minutes, and none depends on another. How long does parallel execution take?**

- 30 minutes
- 15 minutes
- 10 minutes
- 5 minutes

> **Answer:** 15 minutes. Parallel time is the slowest agent: 15 minutes, instead of the 30-minute sum.

**7. Five moderation agents use the same model, same data and same prompt. Does majority voting cut errors much?**

- Yes, by about 40×
- Yes, by about 5×
- Barely: they tend to make the same mistakes together
- Voting needs at least seven agents

> **Answer:** Barely: they tend to make the same mistakes together. Voting only helps when mistakes are independent. Diversity of models, data and approaches is essential.

**8. How does a Strands swarm know it is finished?**

- When an agent completes its turn without handing off
- After exactly 20 handoffs
- When the supervisor says so
- When every agent has run once

> **Answer:** When an agent completes its turn without handing off. No handoff means completion. max_handoffs and the other limits are safety nets, not the normal ending.

**9. Two swarm agents keep passing the task back and forth. Which settings stop that?**

- max_tokens and temperature
- entry_point and node_timeout
- callback_handler=None
- repetitive_handoff_detection_window and repetitive_handoff_min_unique_agents

> **Answer:** repetitive_handoff_detection_window and repetitive_handoff_min_unique_agents. The swarm looks at the last N turns (8 in the lab) and stops if fewer than M different agents (3) appear.

**10. Your payment processor asks you to prove that high-value orders always get reviewed. Which pattern makes that easiest?**

- Swarm
- Supervisor–worker
- Graph
- A single agent

> **Answer:** Graph. In a graph the routing is explicit in code (conditional edges), so you can point at the exact path every high-value order takes.

Score: 0 of 10 answered

> **Up next: Section 5, MCP and A2A:**
> So far your agents have lived in one notebook. Next you'll connect them across processes with two open protocols: **MCP**, which connects an agent to tools and data served by other programs, and **A2A**, which lets independent agents discover and call each other. Folder: `section-05-mcp-and-a2a`.
