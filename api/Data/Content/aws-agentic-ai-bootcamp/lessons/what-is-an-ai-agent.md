# What is an AI agent?

## 1.2 What is an AI agent?

An agent is someone, or something, that does a task on your behalf. An AI agent uses an LLM to reason, plan and carry out tasks for people or for other systems.

**AI agents** are autonomous software systems. Their tasks can be as different as compiling research, paying bills, planning a trip or managing enterprise applications. They make decisions, adapt to new information and take action **without needing a human to spell out every step**. Many of them use RAG as part of their work to fetch the facts they need.

What really makes agents powerful is that they think **iteratively**: they try something, look at the result, adjust their approach, and keep going until the goal is reached.

> **A chatbot:**
> Like the enquiry counter at a railway station. Ask "When does the Shatabdi leave?" and you get an answer. You still have to queue, book, and check the PNR yourself.

> **An agent:**
> Like a personal travel assistant. You say "get me to Chennai by Friday morning". They check trains and flights, book the best option, and message you if it's delayed.

#### An agent as a smart travel planner

A user asks: *"What should I pack for New York in summer?"* A plain chatbot would give generic advice. Watch what an agent does instead: it gathers facts from different places, combines them with what it knows about this user, then decides.

{{diagram:1}}

*Agentic RAG in action. The agent uses RAG for history, an API for live data and memory for this user, then reasons over all three. The answer is personal because the agent decided what to look up, not because someone scripted it.*

#### Agent capabilities: plan, act, reason

RAG made LLMs better at *answering* by adding a retrieval step. Agents build on that foundation and go much further: they make decisions and take actions on their own, even for complex, multi-step tasks. They do it with three abilities, used in a loop:

1. 1 Planning Break a high-level objective into tasks that can actually be executed.
2. 2 Acting Use tools and information (such as knowledge bases) to carry out those tasks.
3. 3 Reasoning Look at the results of each action and update the plan, again and again, until the goal is achieved.

{{diagram:2}}

*Plan, act, reason, repeat. A chatbot stops after one answer. An agent goes round this loop as many times as the task needs.*

For example, an agent could fully automate scheduling a meeting: checking calendars, sending invites, booking a room, following up when someone declines, and updating the details. That is a job you would normally give a human executive assistant. Step through it below and notice the moment the plan has to change.

Try it

##### Watch an agent schedule a meeting

The agent's plan

What happens

Colour key in the log: plan, act, observe and reason.

**Watch an agent schedule a meeting, step by step:**

- **Plan:** Goal: "Set up a 45-minute design review with Priya, Arjun and Meera this week." I'll break it into six tasks.
- **Act:** Calling the calendar API for Priya, Arjun and Meera.
- **Observe:** All three are free on Thu 3:00 to 4:00 pm and Fri 11:00 am to 12:00 pm.
- **Plan:** Choosing Thursday 3:00 pm, the earliest common slot.
- **Act:** Room-booking API: 'Neem' room, Thu 3:00 to 3:45 pm. Booked.
- **Act:** Sending calendar invites to all three.
- **Observe:** Meera declined: "Client call on Thursday afternoon."
- **Plan:** Re-planning. Thursday no longer works, so I'll move to the next common slot and fix the room.
- **Act:** Cancelled 'Neem' for Thursday. Booked 'Peepal' room, Fri 11:00 to 11:45 am.
- **Act:** Sent the updated invite for Friday 11:00 am.
- **Observe:** Priya, Arjun and Meera all accepted.
- **Done:** Added the agenda link to the meeting. Goal achieved ✓

**The plan as it grows:**

1. Check everyone's calendars
2. Find a common free slot
3. Book a meeting room
4. Send invites
5. Follow up on replies
6. Release Thursday's room (new)
7. Re-book for Fri 11:00 am and re-invite (new)
8. Update the meeting details

#### The parts of an agent

Every agent, however fancy, is built from the same few parts. Learn this picture well; the rest of the course fills in each box.

{{diagram:3}}

*The agent is the coordinator, not the brain. The LLM does the thinking; the agent passes messages between the user, the LLM, the tools and memory, and keeps the plan moving.*

| Part | What it does | Examples | Covered in |
| --- | --- | --- | --- |
| Tools | External functions or APIs the agent uses to reach beyond its own knowledge and do things in the world | Search engine, database, calculator, code interpreter, weather API, a RAG pipeline | Section 2 |
| Memory | Stores past interactions, short-term and long-term, so the agent keeps context and sees the bigger picture | This conversation so far; "this user prefers vegetarian food" | Section 3 |
| Planning | Analyses the problem, works out the best order of actions, and decides which tool to use when. Strategy, not random actions | "First check calendars, then book the room, then send invites" | This section, Section 4 |
| LLM | The core intelligence. The agent consults it to understand the request, draft responses and choose the next action, such as which tool to call. The relationship runs both ways | Claude Sonnet 4.6 or Claude Haiku 4.5 on Amazon Bedrock | This section |

> **Think of it like this:**
> An agent is a person at work. The **LLM is the brain**, the **tools are the hands** (phone, laptop, calculator), **memory is the notebook** on the desk, and the **plan is the to-do list**. A brain alone can't send an email; a pair of hands alone doesn't know which email to send. The agent is the whole person.

With this picture of how an agent is put together, let's see how these ideas map onto real services on AWS.

## 1.3 The AWS agentic stack

So far we have talked theory. Now we ground it in real services. AWS offers agent-building services at three levels of effort, and picking the right level is half of building a good agent.

Think of the AWS agentic AI landscape as a spectrum. At one end are ready-made apps for business users. In the middle are managed platforms for developers who want flexibility without running servers. At the other end are highly customisable services and specialised hardware for builders who need deep control.

> **Think of it like this:**
> Dinner, three ways. **Order on Swiggy**: ready to eat, no effort, little choice (agentic applications). **A meal kit**: ingredients prepped and delivered, you cook it your way (managed solutions). **Cook from scratch**: buy the produce, own the kitchen, control every spice (do it yourself). This course cooks with the meal kit.

{{diagram:4}}

*Three tiers, one trade-off. Going down the stack you gain control and pay for it in effort. This course lives in the middle tier: Amazon Bedrock for models and safety features, Amazon Bedrock AgentCore for running agents in production.*

Try it

##### Which tier fits you?

"I run HR. I want AI to summarise policies today, no coding."

"I'm a developer. I want to ship a custom agent fast."

"I'm an ML engineer. I must fine-tune a model and control the hosting."

Pick a person above. The matching tier lights up in the diagram.

**"I run HR. I want AI to summarise policies today, no coding."**

**Agentic applications.** A ready-made app such as Amazon Quick Suite can summarise policies and answer questions with almost no setup. No code needed, but also little control over how it works.

**"I'm a developer. I want to ship a custom agent fast."**

**Managed solutions.** Use Amazon Bedrock for the model and guardrails, a framework like Strands for the agent, and Amazon Bedrock AgentCore to run it in production. This is exactly what this course teaches.

**"I'm an ML engineer. I must fine-tune a model and control the hosting."**

**Do it yourself.** Fine-tune and host the model in Amazon SageMaker AI, on Trainium or Inferentia chips if you need them. You can still bring the result into Bedrock with Custom Model Import and use it as an agent's brain.

#### Tier by tier

##### Agentic applications

The top tier is fully managed, out-of-the-box agentic apps. They need minimal setup and the least effort, so they suit business users or anyone who wants AI quickly without deep technical skills. This tier started as the Amazon Q family (Amazon Q Business, Amazon Q Developer) and is moving to newer apps such as Amazon Quick Suite for business teams and Kiro, an agentic IDE, for developers.

> **We skip this tier:**
> This course is about building agents with code, so we don't use the ready-made apps. Product names in this tier change often (Amazon Q Developer, for example, is being retired in favour of Kiro), so always check the current AWS documentation.

##### Managed solutions

More flexible than ready-made apps, but AWS still hides most of the infrastructure. Moderate effort, ideal for developers building custom agents without assembling every component. The two services we use throughout the course:

**Amazon Bedrock** is the key service for building and scaling generative AI apps. It gives you a choice of high-performing **foundation models** from Amazon and leading AI companies, all through a **single API**. Its features include:

| Bedrock feature | What it does in plain words | In this course |
| --- | --- | --- |
| Foundation models | Ready-to-call models such as Claude, Amazon Nova and Titan, paid per use | Every section |
| Guardrails | Safety policies that block harmful or off-topic input and output | Section 7 |
| Agents | A managed way to create agents that run multi-step tasks | We build agents in code with Strands instead |
| Custom Model Import | Bring your own customised model into Bedrock and call it like any other | Concept only |
| Knowledge Bases | Managed RAG: connects to company data and grounds answers in it | Concept only |
| Model and RAG evaluation | Measures how good a model, a knowledge base or a RAG setup really is | Section 7 (agent evaluation) |

**Amazon Bedrock AgentCore** is a secure, scalable platform for *deploying and operating* agents, so they can use tools and data without you managing infrastructure. It works with any framework (Strands, LangGraph, CrewAI…) and any model, combining open-source flexibility with enterprise-grade security and reliability. Its pieces map neatly onto the rest of this course:

- **Runtime**: a fully managed, low-latency **serverless** environment to deploy agents and tools (Section 6)
- **Memory**: short- and long-term memory for agents (Section 3)
- **Gateway**: turns existing APIs into tools agents can call (Section 6)
- **Observability, Evaluations, Policy**: see, measure and control what agents do (Section 7)
- **Identity**: who the agent is and what it may access on a user's behalf

Bedrock and AgentCore evolve quickly, so for the exact feature list always refer to the latest AWS documentation.

##### Do it yourself

The bottom tier gives maximum control. It provides the foundational infrastructure and tools to build, deploy and scale agentic apps from scratch, for experienced developers, ML engineers and researchers who want a say in everything from hardware to custom model architectures. **Amazon SageMaker AI** is the end-to-end service here: build, train and deploy machine-learning models at scale, including custom model development.

> **Think of Bedrock like UPI:**
> UPI lets any app talk to any bank through one standard. Bedrock lets your code talk to models from many companies through one API. Switching from Claude Sonnet to Claude Haiku is changing one string, which is exactly what the `BEDROCK_MODEL_ID` variable does in our code.

{{diagram:5}}

*One front door, many models. Your agent code never changes when you change models. And if you customise a model in SageMaker AI, Custom Model Import brings it into Bedrock so it can be your agent's brain too.*

> **Customising the brain:**
> You can adapt an LLM to your domain in Amazon SageMaker AI (for example, by fine-tuning on your legal or medical documents) and then make it available in Bedrock through Custom Model Import. That domain-adapted model can then act as the reasoning engine, the "brain", of your agent.

#### Bedrock or SageMaker AI?

Most agent builders live in Bedrock and reach for SageMaker AI only when they need deeper control. Here is the side-by-side view.

| Service | Best suited for | Strengths |
| --- | --- | --- |
| Amazon Bedrock | Rapid development of generative AI apps and agents | Managed, serverless-style access to foundation models; one unified API; agent features; models from many providers |
| Amazon SageMaker AI | Advanced customisation, model training, fine-tuning and specialised deployment | Deep control over training, hosting, tuning and deployment; many endpoint and infrastructure options |

In this course we use **Amazon Bedrock** to build and deploy agents, because it is a managed, API-first way to drive agent workflows with foundation models. SageMaker AI plays a supporting role for teams that need more: the agent's brain might be fine-tuned in SageMaker AI, or hosted on a SageMaker AI **endpoint** when a team wants tighter control over cost, latency or infrastructure. Together they cover everything from quick agent prototypes to heavily customised model deployments.

> **Think of it like this:**
> **Bedrock is booking an Uber**: you pay per trip (per **token**), pick the car type, and never think about servicing. **A SageMaker AI endpoint is leasing your own car**: you choose exactly which car, keep it ready all day, and pay for it even while it's parked, in exchange for full control.
