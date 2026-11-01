# Lab: make agents reusable with "agent as tool"

## 4.4 Lab: make agents reusable with "agent as tool"

Build a specialist once, give it a clear description, and any other agent can discover and call it like an ordinary tool.

Supervisor–worker works well, but if every specialist is built from scratch for one particular supervisor, you rebuild it again and again. The **agent as tool** pattern fixes that: you wrap an agent with a description of what it does, and other agents can call it just like a regular tool. Treating components as modular, reusable tools lets a system grow without rigid dependencies between its parts.

When an agent receives a task, it reads the available tool descriptions and picks the right one, exactly as you saw with tools in Section 2. The only difference is that these tools are agents.

> **Think of it like this:**
> A hospital's specialist doctors. The cardiologist isn't hired by one GP; any doctor in the hospital can refer a patient to them. The referral desk only needs to know "cardiologist: heart problems". Build the specialist once, and every department can use them.

{{diagram:1}}

*The tools are agents. The main agent doesn't know calculus; it knows that "math agent: solves equations" fits the question. Writing and science agents sit unused until a question needs them.*

#### The example: a tutoring assistant

Students ask about different subjects, and you have specialist tutors for math, writing and science. Instead of writing routing logic like *"if the question contains 'equation', call the math tutor"*, you wrap each specialist as a tool and let the teacher agent decide which one to use.

#### Run the notebook: `02_agent_as_tool.ipynb`

Cells 1 and 2 are the same install and model cells as notebook 1. Then:

```python title="cell 3"
from strands import Agent
```

##### Specialist agents

Each specialist gets a `name` and a `description`. When an agent is used as a tool, the name becomes the tool name and the description tells the teacher when to call it.

```python title="cell 4"
math_tutor = Agent(
    name="math_tutor",
    description="Solves mathematical equations and explains math concepts step by step",
    model=model,
    system_prompt="You are a math tutor. Solve math problems and explain your solutions clearly, step by step.",
    callback_handler=None,
)

writing_coach = Agent(
    name="writing_coach",
    description="Helps with writing, grammar, and essay structure",
    model=model,
    system_prompt="You are a writing coach. Help with writing, grammar, and essay structure. Provide constructive feedback.",
    callback_handler=None,
)

science_helper = Agent(
    name="science_helper",
    description="Explains scientific concepts and principles in simple terms",
    model=model,
    system_prompt="You are a science tutor. Explain scientific concepts clearly using simple language and real-world examples.",
    callback_handler=None,
)
```

##### The teacher (**orchestrator**)

Pass the specialist agents straight into `tools=[...]`; Strands wraps each one as a callable tool for you.

```python title="cell 5"
teacher = Agent(
    model=model,
    system_prompt="""You are a teacher who helps students by delegating to specialist tutors.
Never solve problems yourself. Always delegate to the appropriate specialist:
- math_tutor: for math problems and equations
- writing_coach: for writing, grammar, and essays
- science_helper: for science questions

After receiving the specialist's response, present it to the student in a friendly way.""",
    tools=[math_tutor, writing_coach, science_helper],
)
```

> **Two ways to say the same thing:**
> Notebook 1 wrote `tools=[news_agent.as_tool(), …]`. Here it's `tools=[math_tutor, …]`. When Strands finds an agent in the tools list, it calls `.as_tool()` for you with the default settings. Use `.as_tool(name=..., description=...)` explicitly when you want to override the name or description.

##### Test with different questions

```python title="cell 6"
# Math → math_tutor
response = teacher("Can you help me solve this quadratic equation: x^2 + 5x + 6 = 0?")
```

```text title="outputillustrative"
I'll help you with that quadratic equation! Let me connect you with our math specialist.
Tool #1: math_tutor

Great! Here's what our math tutor explained:

To solve x² + 5x + 6 = 0, we can use factoring.

Step 1: Look for two numbers that multiply to 6 and add to 5.
        Those numbers are 2 and 3 (since 2 × 3 = 6 and 2 + 3 = 5).

Step 2: Factor the equation: (x + 2)(x + 3) = 0

Step 3: Solve each factor:
        If x + 2 = 0, then x = −2
        If x + 3 = 0, then x = −3

Solution: x = −2 or x = −3

You can check both answers by substituting them back into the original equation; both make it equal zero!
Would you like help with another problem?
```

The teacher has no hard-coded rule like "if math question, call the math tutor". It saw three tools, read their descriptions, and chose `math_tutor` because the question matched "solves mathematical equations". Then, as its prompt asks, it presented the tutor's answer in a friendly way.

```python title="cell 7"
# Writing → writing_coach
response = teacher("How do I write a strong thesis statement for my essay about climate change?")
```

```python title="cell 8"
# Science → science_helper
response = teacher("Why does ice float on water?")
```

Expect `Tool #1: writing_coach` for the thesis question and `Tool #1: science_helper` for the ice question (ice is less dense than liquid water because its molecules lock into an open crystal structure).

Try it

##### Which tutor does the teacher call?

"Solve x² + 5x + 6 = 0"

"Why did the Mughal Empire decline?"

on Register a `history_tutor` agent as a fourth tool

Pick a question.

| Tutor | Description |
| --- | --- |
| `math_tutor` | Solves mathematical equations and explains math concepts step by step |
| `writing_coach` | Helps with writing, grammar, and essay structure |
| `science_helper` | Explains scientific concepts and principles in simple terms |
| `history_tutor` | Explains historical events, causes and consequences |

- **Math** (`math_tutor`): “Can you help me solve x² + 5x + 6 = 0?” **Tutor:** Factor it: (x + 2)(x + 3) = 0, so x = −2 or x = −3.
- **Writing** (`writing_coach`): “How do I write a strong thesis statement for my essay about climate change?” **Tutor:** Make one specific, arguable claim and preview your main reasons in a single sentence.
- **Science** (`science_helper`): “Why does ice float on water?” **Tutor:** Ice is less dense than liquid water: its molecules lock into an open crystal structure.
- **History** (`history_tutor`): “Why did the Mughal Empire decline?” **Tutor:** Weak successors after Aurangzeb, costly wars, rising regional powers, and the growing strength of European trading companies.

> **Teacher:** reads the three descriptions; none covers history. Its prompt says *never solve problems yourself*, so it replies: “I don't have a history specialist available right now, but I can help with math, writing or science.”
> Tick the checkbox to register history_tutor. No routing code changes.

> **Teacher** matches the question to `<tutor>`'s description and calls it: `Tool #1: <tutor>`. **Tutor:** <answer>. **Teacher:** presents it in a friendly way.

#### Why this is so flexible

Want a history tutor? Create a `history_tutor` agent and add it to the teacher's tools. The teacher automatically knows it exists. No routing logic to update, no new `if` statements.

And it goes deeper. Specialists can have their own tools, including other agents, creating layers of expertise. Your `math_tutor` might use a `calculator_agent` and a `graph_plotter_agent`. And the same `math_tutor` can be reused by a teacher agent, a tutoring-assistant agent and a homework-grader agent:

{{diagram:2}}

*Layers of expertise. One specialist serves many callers, and can itself call other specialists. Each layer only needs to know the descriptions of the layer below.*

> **Supervisor–worker vs agent as tool:**
> They look alike, and in Strands both use agents as tools. The difference is intent. Supervisor–worker is about *coordination*: fan out, then synthesise one answer. Agent as tool is about *reuse*: a self-contained specialist that any orchestrator can pick up, while the orchestrator stays in control of the conversation.

## 4.5 How data flows through a team of agents

You've built two patterns. Now zoom out and follow one request as it moves through a multi-agent system, step by step.

The request: *"What's the best laptop for video editing under ₹1,80,000?"*

{{diagram:3}}

*One question, many hands. A router fans the request out, specialists work in parallel (and occasionally consult each other), and an aggregator merges everything into one reply.*

Step through

##### Follow the laptop question

Pick step 1.

- **Step 2:** The **router** decides it needs specs, prices and reviews, and rephrases for each: the specs agent gets “What CPU and GPU are needed for 4K editing?”, the price agent “Find laptops under ₹1,80,000 with these specs”.
- **Step 3:** All three specialists work **at the same time**. Each keeps its own memory of the conversation.
- **Step 4:** The price agent found one at ₹1,65,000, but the specs agent says it lacks RAM for 4K. They negotiate: “Can we stretch to ₹1,90,000?”
- **Step 5:** The **aggregator** collects: 32 GB RAM and a recent dedicated GPU needed; three matches at ₹1,72,000, ₹1,79,000 and ₹1,86,000; the ₹1,79,000 model rated 4.5 stars for rendering.
- **Step 6:** “I recommend Laptop B at ₹1,79,000: right specs, within budget, praised for rendering speed.” One answer, three specialists behind it.

1. 1 The request arrives The question enters the system as raw text. Nothing has happened yet.
2. 2 The router makes decisions It reads the question and thinks: *"This person needs product recommendations, price comparisons and technical specs. I know which agents can help."* It sends work to the **specs agent** (knows what video editing needs), the **price agent** (searches current prices across retailers) and the **review agent** (analyses customer feedback). It doesn't forward the question blindly; it rephrases it for each. The specs agent gets *"What CPU and GPU are needed for 4K video editing?"*; the price agent gets *"Find laptops under ₹1,80,000 with these specs."*
3. 3 The agents do their thing All three work at the same time: one works out requirements, one searches retailer listings, one reads thousands of reviews. Each agent can keep its own memory of the conversation (in Strands, wrap it with `as_tool(preserve_context=True)`; the default starts each call fresh), so if you mentioned your editing software earlier, the specs agent remembers.
4. 4 Agents talk to each other (sometimes) The price agent finds a laptop at ₹1,65,000, but the specs agent realises it doesn't have enough RAM for 4K. The price agent asks: *"If we stretch the budget to ₹1,90,000, can we get something that works?"* Agents negotiate and refine based on what the others find. (In a strict supervisor–worker setup this exchange goes through the supervisor; in collaborative setups, covered next, agents talk directly.)
5. 5 Results are combined An aggregator (often the supervisor) collects: specs agent: *"At least 32 GB RAM, a recent mid-range dedicated GPU and a fast multi-core CPU."* Price agent: *"Three laptops match: ₹1,72,000, ₹1,79,000 and ₹1,86,000."* Review agent: *"The ₹1,79,000 one is rated 4.5 stars, with praise for rendering speed."*
6. 6 You get your answer *"I recommend Laptop B at ₹1,79,000. It meets the specs for 4K editing, fits your budget, and users specifically praise its rendering performance."* It feels like one agent answered, but three specialists collaborated behind the scenes.

A single agent would have to know video-editing requirements, search several retailers, analyse reviews and synthesise everything itself: slower, more expensive and more likely to miss something. With several agents, each is an expert in its area, and they work in parallel. That raises the obvious next questions: how do agents share information, and how do you decide whether they work in sequence, in parallel or together?

## 4.6 How agents talk to each other

Agents working in isolation aren't a system; they're just separate programs. Communication is what turns them into a team.

Agents communicate in three main ways. Each solves a different problem and fits a different situation.

#### Sequential communication

Think of writing a research paper. You can't write the conclusion before the research, and you can't edit what hasn't been written. Some things must happen in order. In **sequential** communication, one agent finishes and hands its results to the next.

{{diagram:4}}

*A relay race. Each agent waits for the previous one; total time is the sum of every step.*

The research agent might spend 10 minutes gathering information, the writing agent 15 minutes drafting, and the editing agent 5 minutes polishing: 30 minutes in total. The writing agent literally cannot start without the research, and the editor needs a complete draft.

> **Use it when:**
> There are real dependencies: step B needs step A's output. Bonus: only one agent calls the LLM at a time, which helps if your account has API **rate limits**.

> **The cost:**
> Time adds up with no overlap. And if the writing agent fails after 10 minutes of research, that time is wasted: everything downstream stops and the pipeline has to restart.

#### Parallel communication

Now picture planning a conference: one person books the venue, another arranges catering, a third handles marketing. None depends on the others, so they happen at the same time. In **parallel** communication, several agents work simultaneously on different parts of a problem, and their results are combined when all have finished.

{{diagram:5}}

*Everyone at once. Total time is the time of the slowest agent, not the sum.*

Say you're analysing a market before a product launch and need three kinds of analysis. One agent scrapes a competitor's website and builds a pricing matrix (5 minutes). Another reads thousands of customer reviews of similar products, finding patterns in complaints and praise (5 minutes). A third analyses search trends, social media mentions and industry reports (5 minutes). Run them one after another and you wait 15 minutes; run them in parallel and you wait 5, the time of the slowest agent.

Parallel works best when tasks are **independent**: agent 1 doesn't need agent 2's results. It's also useful for **accuracy**, with several agents checking the same thing from different angles.

Try it

##### Sequential vs parallel timing

Agent A takes 10 min 10

Agent B takes 15 min 15

Agent C takes 5 min 5

on B needs A's output, C needs B's

Sequential

Parallel

> **Sequential: <sum> min. Parallel: <slowest> min** (the slowest agent). Saved <difference> min, <percent>% faster, because nobody waits for anybody.

> **Sequential: <sum> min. Parallel: impossible here.** B needs A's output and C needs B's, so the work is forced into a sequence. Untick the dependency to see parallel speed-up.

##### Parallel for accuracy: let agents vote

Imagine a content-moderation system. Three agents independently check whether a post breaks community guidelines. Agent 1 says safe, agent 2 says safe, agent 3 says unsafe. Two of three vote safe, so the post is approved.

Agents make mistakes, but if they're independent they don't all make the *same* mistakes. If two of three agree, you can trust the result more than any single opinion; if all three flag something, you can be very confident it needs review. The maths backs this up: if each agent is wrong 5% of the time, independently, a majority vote of five agents is wrong only about 0.12% of the time, because at least three would have to be wrong together.

{{diagram:6}}

*Majority voting. One agent's mistake is outvoted by the other two, as long as their mistakes are independent.*

| Voting rule | How it decides | Fits |
| --- | --- | --- |
| Simple majority | More than half agree | Content moderation |
| Unanimous | All agents must agree | High-stakes calls such as a medical-diagnosis assistant |
| Weighted | Some votes count more | Legal document review, where the specialist agent's vote weighs more |

> **Voting only works with independent agents:**
> If every agent uses the same model, the same data source and the same reasoning, they'll make the same mistakes and voting adds nothing. You need diversity: different models, different data sources, different approaches.

Try it

##### How much does voting help?

Each agent's error rate = 5% 5

Number of voting agents

on All agents use the same model and data (correlated mistakes)

One agent alone is wrong

Majority vote is wrong

> With one agent there's nothing to outvote: the system is exactly as reliable as that agent.

> **No improvement.** Agents with the same model, data and reasoning make the same mistakes at the same time, so they outvote nothing. Diversity is what makes voting work.

> **<ratio>× fewer wrong decisions.** The vote is only wrong when at least <k> of <n> agents are wrong on the same item, which is much rarer than one being wrong. (Careful: if each agent is wrong half the time or more, voting makes things worse.)

#### Collaborative communication

Think about designing a building. The architect proposes a design; the structural engineer says it won't bear the load; the architect adjusts; the interior designer suggests changes for better flow. They go back and forth until the design satisfies every constraint. In **collaborative** communication, agents talk to each other, share insights, negotiate trade-offs and refine their work together.

Here three agents review code: a **developer** agent wrote a function that processes user data, a **security** agent checks for vulnerabilities, and a **performance** agent makes sure it's fast enough. Step through their negotiation:

{{diagram:7}}

*A real conversation. Unlike sequential (one direction) or parallel (no talking), collaborative agents push back on each other until every concern is met.*

Step through

##### A code review negotiation

Security: open Performance: open Memory use: not checked

#### Read the whole conversation

1. **Developer:** I've written a function that processes user data quickly.
2. **Security:** This is vulnerable to SQL injection. You need to sanitise inputs.
3. **Developer:** If I add sanitisation, performance drops by 40%.
4. **Performance:** 40% slower is unacceptable. We have strict latency requirements.
5. **Security:** Then use parameterised queries. They're secure and fast.
6. **Developer:** Good idea. Let me refactor.
7. **Performance:** Wait, you're loading the entire dataset into memory. Stream it instead.
8. **Developer:** Done. All three concerns addressed.
9. *All agents review the updated code.*
10. **Security:** Secure now. **Performance:** Meets latency requirements. **Developer:** Code is ready.

Round complete: secure, fast and memory-safe, because each agent pushed back until its constraint was met.

This back-and-forth doesn't happen in sequential or parallel setups. Sequential passes information one way; parallel agents work without talking. Collaboration is a real conversation that continues until the solution satisfies every agent's requirements, here balancing security, performance and maintainability. And it does work better on hard problems: experiments with multi-agent discussion show that iterative debate catches errors and explores alternatives a single agent would miss.

> **Use it when:**
> Agents must balance trade-offs with no single right answer: security vs performance, cost vs quality, speed vs accuracy. Decisions where one agent's recommendation affects another's.

> **The cost:**
> Several rounds of discussion means several rounds of LLM calls. One agent might answer in 10 seconds; three collaborating might take 30 to 40. It's slower, costlier, and harder to troubleshoot: finding which round introduced a bad decision takes more work than debugging a simple pipeline.

| Technique | Information flows | Time | Best for |
| --- | --- | --- | --- |
| Sequential | One direction, A → B → C | Sum of all steps | Real dependencies; tight rate limits |
| Parallel | Out to everyone, then combined | The slowest step | Independent tasks; accuracy through voting |
| Collaborative | Back and forth, in rounds | Several rounds of calls | Trade-offs with no single right answer |

Sequential, parallel and collaborative are the building blocks. Next you'll see how whole systems are organised around them.
