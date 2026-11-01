# Strands Agents and the agent loop

## 1.7 Strands Agents and the agent loop

You now know the parts of an agent and the protocols around it. To actually build one, you need a framework that wires those parts together. In this course that framework is Strands Agents.

An agent framework gives you the building blocks: a way to define and orchestrate tools, store memory, and configure the LLM. As we saw in 1.4, popular frameworks include LangChain (with LangGraph) and Strands. We use Strands to build our "Hello World" agent, and here's why it feels so simple.

**Strands Agents** is an open-source **SDK** from AWS that takes a **model-driven** approach to building and running agents with very little code. You describe the goal and hand over the tools; the LLM (for example, one on Amazon Bedrock) plans, reasons and chooses tools by itself.

{{diagram:1}}

*Who decides the steps? In workflow-driven code, you do, in advance, for every case. In model-driven code, the model decides at run time, using the tool descriptions you provide.*

> **Think of it like this:**
> Workflow-driven is giving a new driver turn-by-turn directions: if a road is closed, they're stuck. Model-driven is telling an experienced cab driver "Kempegowda airport, fastest route": they pick the roads, check traffic and reroute on their own.

#### Why Strands

| Feature | What it means for you | Where you'll see it |
| --- | --- | --- |
| Agents in a few lines | Define a prompt and some tools; that's an agent | This section |
| Easy tool integration | Turn any Python function into a tool, or use prebuilt and external tools and APIs | This section, Section 2 |
| Model-agnostic | Works with many LLM providers, including Amazon Bedrock, Anthropic and more | `BedrockModel` in every lab |
| Multi-agent workflows | Build complex flows where several agents collaborate | Section 4 |
| Safety and monitoring | Hooks for guardrails, prompt security and watching agent performance | Section 7 |

#### Inside Strands: the agent loop

This is the most important picture in the section. Every Strands agent, from the ten-line hello world to a production system, runs this loop. It's also called the **agentic loop** or agentic workflow: take a high-level prompt, use a model to reason, use tools to act, and deliver a result.

{{diagram:2}}

*The loop that makes it an agent. The agent keeps going round: ask the model, run whatever tool it asks for, give the result back, ask again. It exits only when the model answers without asking for a tool.*

##### Walking through the loop with a story prompt

Say the user's prompt is *"Write a short story about a robot who wants to be a painter."* That's the goal. Here is what happens, step by step.

1. 1 Invoke the agent The prompt is sent to the agent, the central orchestrator. Its job is to understand the prompt, plan how to fulfil it, and manage the conversation with the model and the tools.
2. 2 Enter the agentic loop Everything inside the dashed box is the loop, where the thinking and acting repeat.
3. 3 Invoke the model The agent sends the prompt (or a refined version, plus the conversation so far) to the model, the LLM.
4. 4 Get a response The model generates text based on its input.
5. 5 Reasoning The model understands the prompt, breaks it down and decides the next step. It might reason: *"To write a story I need a character, a setting, a plot and an ending. I might want to look up some art ideas."*
6. 6 Tool selection The model decides whether it needs an external tool. If the prompt had asked for an illustration too, it might choose an image generation API.
7. 7 Execute the tool If the model asks for a tool (to find information, make an image, do a calculation), the agent runs it. Tools are the external APIs or functions the agent has access to: image generation, text-to-speech, a search engine. For a plain story the model may need no tool; for *"…and include an image of the robot's first painting"* the agent would call the image API here.
8. 8 Return the result The tool does its job and sends its result back to the agent.
9. 9 Go round again With the tool result (or straight away, if no tool was needed) the agent calls the model again with the updated context. Ask the model, the model reasons and maybe picks a tool, the agent runs it, the result goes back in. This repeats until the prompt is fully handled.
10. 10 Return the final response When the work is done, the agent collects everything, including the story written by the model.
11. 11 Result The agent hands the result back to the user: the complete short story about the robot who wants to be a painter.

Run it

##### Agent loop simulator, using the prompts from our notebook

{{diagram:3}}

Tool results are real: the time comes from your browser clock and the maths is actually computed.

**Walkthrough: "Explain AgentCore (no tools)"**

- **Agent:** Receives the prompt and adds it to the conversation.
- **Agent:** Invokes the model with 1 message and no tools.
- **Result:** Model replies. stop_reason = end_turn: it answered directly, no tool needed.
- **Model reply:** "Amazon Bedrock AgentCore is a set of managed services for deploying and operating AI agents securely at scale. It works with any framework, such as Strands or LangGraph, and any model. Pieces like Runtime, Memory, Gateway, Identity and Observability handle the infrastructure so you can focus on the agent's logic."
- **Done:** Loop ends after one pass. Final response returned to you.

**Walkthrough: "Time in Bangalore and New York"**

- **Agent:** Receives the prompt.
- **Agent:** Invokes the model, offering one tool: current_time.
- **Result:** Model replies. stop_reason = tool_use: it wants current_time twice, once per city.
- **Model reply:** "I'll check both time zones."
- **Agent:** Executes current_time("Asia/Kolkata") and current_time("America/New_York").
- **Result:** Tools return the current time for each city.
- **Agent:** Invokes the model again, now with the tool results in the history.
- **Result:** Model replies. stop_reason = end_turn.
- **Model reply:** "Right now it's … in Bangalore, and … in New York."
- **Done:** Loop ends after two passes. Final response returned to you.

**Walkthrough: "18% GST on Rs 84,999"**

- **Agent:** Receives the prompt.
- **Agent:** Invokes the model, offering two tools: calculator and current_time.
- **Result:** Model replies. stop_reason = tool_use: it wants calculator twice, and ignores current_time.
- **Agent:** Executes calculator("84999 * 0.18") and calculator("84999 * 1.18").
- **Result:** Tools return: 15299.82 and 100298.82.
- **Agent:** Invokes the model again with both results.
- **Result:** Model replies. stop_reason = end_turn.
- **Model reply:** 18% GST on Rs 84,999 is Rs 15,299.82, so the final price is Rs 1,00,298.82.
- **Done:** Loop ends after two passes. Final response returned to you.

**Walkthrough: "Robot painter story"**

- **Agent:** Receives the prompt.
- **Agent:** Invokes the model. The model reasons: a character, a setting, a plot, an ending. No tool needed.
- **Result:** Model replies. stop_reason = end_turn, with the story text.
- **Model reply:** "Unit R-7 swept the gallery floor every night, and every night it stopped in front of the same sunset…"
- **Done:** Loop ends after one pass. Had the prompt asked for an illustration, the model would have requested an image tool and the loop would have gone round again.

What the agent is doing

Conversation history the model sees (grows on every step)

[]

> **New word: stop reason:**
> Every model response comes with a **stop reason** that tells the agent what to do next. `tool_use` means "I need a tool, run it and come back to me". `end_turn` means "I'm done, here's my answer". That single field is what keeps the loop going or ends it.

> **Strands in one sentence:**
> Strands has three core ingredients, a **model**, **tools** and a **prompt**, plus the **agentic feedback loop** that lets the agent adapt to changing situations, handle the unexpected, and improve its result with every pass round the loop. Now let's build one.
