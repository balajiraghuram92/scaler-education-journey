# Recap and self-check

## 1.9 Recap and self-check

You now have the foundation every later section builds on.

We traced how agentic intelligence grows, from a plain LLM to teams of agents. RAG gives a model fresh, private knowledge by retrieving the right chunks before it answers. Agents go further: they plan, act with tools, reason about results, and loop until the job is done. We looked at the protocols that let agents plug into tools (MCP) and into each other (A2A), and at why they complement each other.

We mapped the AWS agentic stack and saw why Amazon Bedrock (with AgentCore) and Amazon SageMaker AI cover everything from quick prototypes to heavily customised models. Then we moved from theory to practice with the Strands Agents SDK, its model-driven agent loop, and your own Hello World agent: one line to create it, a decorator to give it a tool, a prebuilt calculator, and a system prompt to shape it.

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| RAG | Retrieve relevant chunks, add them to the prompt, let the model generate from them |
| Chunk, embedding, vector DB | Small pieces of text, their meaning as numbers, and a store that finds the nearest ones fast |
| Agent | An LLM in a loop with tools and memory: plan, act, reason, repeat |
| AWS agentic stack | Ready-made apps, managed services (Bedrock, AgentCore), or do-it-yourself (SageMaker AI) |
| Six stages | LLM, LLM + RAG, augmented LLM, agentic workflow, autonomous agent, multi-agent; risk grows with each |
| MCP vs A2A | MCP connects an agent to tools; A2A connects agents to agents; use both |
| Strands agent loop | Invoke model, run requested tools, return results, repeat until `end_turn` |
| Hello World agent | `Agent(model=BedrockModel(...), tools=[...], system_prompt=...)` |

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

Score: 0 of 10 answered

> **Up next: Section 2, agent tools:**
> You've given your agent a brain. Next you give it hands: building your own tools with `@tool`, using prebuilt and AWS-aware tools like `use_aws`, and advanced patterns such as class-based and async tools. Folder: `section-02-agent-tools`.

**Self-check: the answer explanations, and the questions the quiz shows:**

**Question 4 explanation:** The agent coordinates, the tools act, memory remembers, but the LLM does the understanding, reasoning and deciding.

**Question 5:** Which tier of the AWS agentic stack does this course mainly use?

- Agentic applications such as Amazon Quick Suite
- Managed solutions: Amazon Bedrock and Amazon Bedrock AgentCore
- Do-it-yourself: training models from scratch on Trainium
- None, everything runs locally

**Explanation:** We build agents in code with Strands, call models on Bedrock, and deploy and govern them with AgentCore.

**Question 6:** Your agent must call a weather API exposed by an MCP server, and also ask another company's booking agent to find flights. Which protocols?

- MCP for both
- A2A for both
- MCP for the weather API, A2A for the booking agent
- HTTP for both, protocols are optional

**Explanation:** MCP connects an agent to tools; A2A connects an agent to other agents. They're complementary, and real systems use both.

**Question 7:** In the Strands loop, the model replies with stop_reason = tool_use. What happens next?

- The agent returns the answer to the user
- The agent runs the requested tool and sends the result back to the model
- The agent restarts the conversation
- The agent asks the user which tool to run

**Explanation:** tool_use means "run this and come back". The loop only ends on end_turn.

**Question 8:** In a @tool function, what does the model mainly read to decide whether to call it?

- The function body
- The docstring and the type hints
- The file name
- The return value from last time

**Explanation:** The model never sees your code. It sees the name, the description (from the docstring) and the input schema (from the type hints).

**Question 9:** What's the key difference between an agentic workflow and an autonomous agent?

- Workflows use tools; autonomous agents don't
- A workflow finishes when its goal is achieved; an autonomous agent keeps looping with long-term objectives and self-correction
- Autonomous agents can't use memory
- There is no difference

**Explanation:** A workflow has a finish line. An autonomous agent perceives, acts, learns and self-corrects continuously, which is why it needs the strongest guardrails.

**Question 10:** You get "ValidationException: on-demand throughput isn't supported" calling Claude. The likely fix?

- Request a quota increase
- Use an inference-profile model ID such as global.anthropic.claude-sonnet-4-6
- Switch Region to ap-south-1
- Reinstall boto3

**Explanation:** Newer models are called through inference profiles. IDs with the global. or us. prefix route the request for you.

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 1. Course code is provided under the MIT License.

AWS service names and features change often. When something here differs from the console, the current AWS documentation wins.

- **Large language model (LLM)** — A model trained on huge amounts of text to predict the next word. That one skill lets it answer, write, summarise and reason. Claude is an LLM.
- **Training** — The one-time, expensive process in which a model learns from data. After training, its knowledge is frozen until someone trains it again.
- **Fine-tuning** — Training an existing model a little more on your own examples so it adapts to your domain or style. Powerful, but slower and costlier than RAG or tools, and it goes stale as your data changes.
- **Knowledge base** — The collection of information a RAG system searches: documents, wiki pages, database rows and so on.
- **Prompt** — The text you send to a model. In RAG, the prompt carries both the retrieved context and the user's question.
- **Ingestion** — Loading documents into a system so they can be processed: reading PDFs, crawling pages, pulling database rows.
- **Chunk** — A small piece of a larger document, often a few hundred words. RAG stores and retrieves chunks rather than whole documents.
- **Context window** — The most text (counted in tokens) a model can take in one request, including your prompt and its answer.
- **Lost-in-the-middle effect** — LLMs tend to use information at the start and end of a long input more reliably than information buried in the middle.
- **Embedding** — A list of numbers that represents what a piece of text means. Texts with similar meanings get similar lists.
- **Vector** — An ordered list of numbers, like [0.21, -0.11, 0.87]. An embedding is a vector.
- **Vector database** — A database built to store vectors and quickly find the ones closest to a given vector. Examples: Amazon OpenSearch Service, Pinecone, pgvector.
- **Similarity search** — Finding the stored vectors closest to a query vector, which means finding the text closest in meaning to the question.
- **Top k** — The k best matches returned by a search. With k = 3 you get the three most similar chunks.
- **Reranking** — A second, more careful scoring pass over retrieved results that puts the truly relevant ones first.
- **Grounding** — Making a model answer from supplied facts, such as retrieved documents, instead of from memory. It reduces made-up answers.
- **AI agent** — Software that uses an LLM to plan, call tools, look at the results and keep working towards a goal without step-by-step instructions.
- **Foundation model (FM)** — A large, general-purpose model trained on broad data and usable for many tasks. On Bedrock: Claude, Amazon Nova, Llama and others.
- **Serverless** — You use a service or run code without managing servers. AWS handles capacity and scaling; you pay for what you use.
- **Endpoint** — A network address where a deployed model waits for requests. A SageMaker AI endpoint is a model you host and keep running.
- **Token** — The unit LLMs read and write: roughly three-quarters of an English word. Prices and limits are counted in tokens.
- **Model as a service (MaaS)** — You call a ready-hosted model through an API and pay per use, with no infrastructure to manage. Amazon Bedrock works this way.
- **Platform as a service (PaaS)** — The platform gives you tools to host and run models, but you choose the model and its compute. SageMaker AI hosting works this way.
- **IDE** — Integrated development environment: the app where you write and run code, such as VS Code, SageMaker Studio or Kiro.
- **Framework** — A library that gives you ready-made structure for a kind of program. Agent frameworks handle the loop, tools, memory and model calls.
- **API** — Application programming interface: a defined way for one program to ask another to do something, usually over a network.
- **STDIO** — Standard input and output. Two programs on the same machine exchange messages by writing to and reading from each other's text streams.
- **HTTP(S)** — The protocol of the web. Programs on different machines send requests and responses over the network; the S means encrypted.
- **Protocol** — An agreed set of rules for how two systems talk: the message format, the order of messages, and what each one means.
- **Client-server** — A design in which a client sends requests and a server answers them. Your browser is a client; a website is a server.
- **Orchestrator** — The component that coordinates the others: decides who does what, in what order, and combines the results.
- **Agent Card** — A JSON document in which an A2A agent describes itself: its name, address, capabilities and skills.
- **JSON** — A simple text format for structured data: {curly braces} for objects, [square brackets] for lists. The common language of APIs.
- **SDK** — Software development kit: a package of libraries and tools for building on a particular platform or service.
- **Agentic loop** — The repeating cycle inside an agent: ask the model, run any tool it asks for, feed the result back, ask again until it's done.
- **Stop reason** — A field on every model response saying why it stopped: end_turn (finished), tool_use (wants a tool), max_tokens (hit the length limit).
- **Inference profile** — A Bedrock model ID that can route requests across AWS Regions for capacity. IDs starting with global. or us. are inference profiles.
- **IAM** — AWS Identity and Access Management: decides who can do what in your AWS account.
- **Virtual environment** — A private folder of Python libraries for one project, so different projects don't clash over versions.
- **STS** — AWS Security Token Service. Its get_caller_identity call tells you which account and identity your credentials belong to.
- **Kernel** — The process that actually runs the code in a Jupyter notebook. Restarting it clears memory and reloads libraries.
- **Streaming** — Sending a response piece by piece as it's generated, instead of all at once at the end.
- **Decorator** — A line starting with @ placed above a Python function to add behaviour. @tool turns a function into an agent tool.
- **Type hints** — Annotations like timezone: str that say what type a value should be. Strands turns them into the tool's input schema.
- **Docstring** — The text in triple quotes at the top of a function describing what it does. For tools, the model reads it to decide when to call the tool.
- **System prompt** — Standing instructions that apply to every turn: the agent's role, tone and rules.
- **ReAct** — Reason + Act: a pattern in which the model alternates between thinking, calling a tool and observing the result.
