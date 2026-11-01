# Quick start with Strands Agent Builder

## 2.6 Quick start with Strands Agent Builder

You can now write tools by hand, use prebuilt ones and reach AWS. But when you just want to test an idea quickly, writing the imports and setup every time slows you down. Agent Builder removes that friction.

**Agent Builder** is a **command-line tool**: you describe what you want in plain English, and it builds and tests it for you. No imports, no setup. It's made for rapid prototyping and learning.

> **Think of it like this:**
> Training wheels on a bicycle. You get to ride and explore right away without worrying about balance. Once you're confident, the training wheels come off and you write your own agents with full control.

Install it with **pipx** (or pip), then start it:

```pseudo title="terminal"
RUN pipx install strands-agents-builder   // or: pip install strands-agents-builder
RUN strands                               // start interactive mode
RUN strands "Build a tool that converts Celsius to Fahrenheit"   // build it from one request
```

```bash reveal title="terminal"
pipx install strands-agents-builder     # or: pip install strands-agents-builder
strands                                 # interactive mode
strands "Build a tool that converts Celsius to Fahrenheit"
```

Watch

##### An Agent Builder session (illustrative)

```text title="terminal"

```

$ export STRANDS_MODEL_ID=global.anthropic.claude-sonnet-4-6
$ strands
Welcome to Strands Agents Builder

~ Build a tool that converts Celsius to Fahrenheit
I'll create that tool and test it.

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32

Testing: What's 100°C in Fahrenheit?
→ 100°C is 212°F

Want to try another conversion?
~ What's 37°C in Fahrenheit?
→ 37°C is 98.6°F

A replay of what a session looks like. The exact wording and generated code will differ each time you run it.

Ask it to "Build a tool that converts Celsius to Fahrenheit", and Agent Builder will:

1. 1 Create the conversion tool
2. 2 Test it with an example For instance, "What's 100°C in Fahrenheit?"
3. 3 Show you the result 100°C is 212°F.
4. 4 Let you keep trying more conversions

#### Two modes

> **Interactive mode:**
> Run `strands` and have a conversation with the builder. Ask it to create tools, test agents or explain concepts.

> **Command mode:**
> Give one instruction directly: `strands "Build a tool that monitors API rate limits across all services and alerts at 80% capacity"`

#### What it comes with

| Kind of agent | Built-in tools it uses |
| --- | --- |
| Data processing | Calculator, Python REPL, file editor |
| Web-connected | HTTP requests, Slack |
| AWS-integrated | `use_aws` to manage cloud resources |
| Multi-agent | `swarm` and `workflow` to coordinate several agents |
| Creative | Image generation and video creation powered by Amazon Bedrock |

#### Under the hood

{{diagram:1}}

*No magic. Agent Builder is a Strands agent with a big toolbox and a good system prompt. It just does the setup for you.*

> **Point it at the course model:**
> Agent Builder uses Amazon Bedrock by default and reads the model ID from the `STRANDS_MODEL_ID` environment variable. Its built-in default is an older Claude Sonnet model, so set it to the one the course uses:

```pseudo title="terminal"
SET STRANDS_MODEL_ID = global.anthropic.claude-sonnet-4-6   // the model the course uses, for this shell
RUN strands                                                   // the builder now uses that model
```

```bash reveal title="terminal"
export STRANDS_MODEL_ID=global.anthropic.claude-sonnet-4-6
strands
```

#### Keeping what you build

Agent Builder runs interactively and does **not** save the generated tool code to files on its own. Two ways to keep your work:

- Start it with `--kb <knowledge-base-id>` (or set `STRANDS_KNOWLEDGE_BASE_ID`) to store and retrieve tools across sessions using an Amazon Bedrock **Knowledge Base**.
- Copy the generated code from the session into your own Python files.

Agent Builder is great for learning and experiments. For production applications you'll want the full control of writing agents yourself, with the patterns from this section.

## 2.7 Tools in LangChain

If you've searched for how to build agents, you've met LangChain. It's been around longer and has a big community, so it's worth knowing how it compares.

Both frameworks do the same core thing: turn Python functions into tools and let agents use them. The difference is approach. Strands is model-driven: you write minimal code and let the LLM work out the workflow. LangChain gives you more explicit control over how the agent executes, which means more setup code but more ways to customise. You already ran a LangChain agent in Section 1; here is its tool next to one from this section:

```pseudo title="Strands (this section, shortened)"
IMPORT Agent and tool
DEFINE check_inventory(product_id)   // @tool: the model reads the docstring and parameters
    // body left out in this shortened example
CREATE agent = Agent(model, tools = [check_inventory])
ASK agent: "Is PROD-123 in stock?"
```

> **Imported:**
> - `Agent` from `strands`: the class that runs the model together with its tools.
> - `tool` from `strands`: the decorator that registers a function as a tool.

```python reveal title="Strands (this section, shortened)"
from strands import Agent, tool

@tool
def check_inventory(product_id: str) -> str:
    """Check if a product is in stock.

    Args:
        product_id: The product ID to check (e.g., "PROD-123")
    """
    ...

agent = Agent(model=model, tools=[check_inventory])
agent("Is PROD-123 in stock?")
```

```pseudo title="LangChain (excerpt, section-01 hello_langgraph_agent.py)"
IMPORT tool from langchain.tools
// a simple tool the agent can call
DEFINE greet(name)   // @tool
    RETURN "Hello, " + name + "! Welcome to the world of AI agents."

CREATE agent = create_agent(llm, tools = [greet], system_prompt = "You are a friendly assistant.")
CALL agent.invoke with the message "Please greet Alice and Bob."
SAVE the result in response
```

> **Imported:**
> - `tool` from `langchain.tools`: the LangChain decorator that registers a function as a tool.

```python reveal title="LangChain (excerpt, section-01 hello_langgraph_agent.py)"
from langchain.tools import tool

# A simple tool the agent can call
@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to the world of AI agents."

agent = create_agent(model=llm, tools=[greet], system_prompt="You are a friendly assistant.")

response = agent.invoke({"messages": [{"role": "user", "content": "Please greet Alice and Bob."}]})
```

|  | Strands Agents | LangChain |
| --- | --- | --- |
| Making a tool | `@tool` + type hints + docstring | `@tool` + type hints + docstring (same idea) |
| Approach | Model-driven: minimal code, the LLM plans the workflow | Explicit control over execution; more setup, more customisation |
| AWS fit | Native: Bedrock, `use_aws`, Lambda, S3 out of the box | Via `langchain-aws` integrations |
| Ecosystem | Growing, AWS-backed | Larger and older community |

We use Strands in this course because it's simpler to learn and fits naturally with AWS services like Bedrock, Lambda and S3. If you work in another environment or need LangChain's larger ecosystem, the tool ideas you learned here transfer directly.

## 2.8 Recap and self-check

Your agents no longer just talk about solutions. They carry them out.

We started with the problem: LLMs are great at generating text but can't check databases, call APIs or touch the real world. We solved it with tools. You turned Python functions into tools with `@tool`, gave one agent several tools and watched it choose the order, used the prebuilt Strands toolbox, and reached S3, DynamoDB and Lambda in plain English with `use_aws`. You built custom tools for your own logic, learned when to group tools in a class or make them async, and saw Agent Builder do the setup for you.

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| Why tools | Without them an agent tells you how; with them it does it |
| Brain, coordinator, hands | The LLM decides, the agent coordinates, tools act |
| Function to tool | `@tool` + type hints + docstring; the model sees name, description and input schema, never the body |
| Many tools | Small single-purpose tools; the agent picks the order and passes data between them |
| Tool ecosystem | Community package, custom tools, MCP tools, AWS integrations, all in one `tools=[…]` list |
| `use_aws` | English to boto3 calls; confirmation for changes; IAM still decides what's allowed |
| Class tools | Share an expensive resource (like one DB connection) across tool methods |
| Async tools | Independent slow calls run concurrently: total time ≈ slowest call, not the sum |
| Agent Builder | A ready-made Strands agent for quick experiments; write your own for production |

#### When something goes wrong

| What you see | What it usually means and how to fix it |
| --- | --- |
| "…is deprecated" warnings from `calculator`, `http_request` or `current_time` | Expected with `strands-agents-tools` 0.8.x. The tools still work; carry on. |
| The notebook pauses asking you to confirm a file write or AWS change | That's tool consent. Answer in the prompt, or set `os.environ["BYPASS_TOOL_CONSENT"] = "true"` as notebook 2 does (sandbox only). |
| `AccessDenied` from S3, DynamoDB, Lambda or IAM | Your user or role lacks that permission. Use an admin sandbox user or attach `setup/iam-policy-course.json`. |
| Lambda creation fails with "role … cannot be assumed" | The new IAM role hadn't propagated yet. Wait a few seconds and re-run the setup cell (it already sleeps 10 s). |
| The agent says it can't do something you gave it a tool for | Check the tool is in `tools=[…]` and the docstring clearly says what it does and when to use it. |
| `ModuleNotFoundError` | Run the `%pip install -q -r requirements.txt` cell, then restart the kernel. |

> **Did you clean up?:**
> If you ran notebook 2, make sure its last cell (3.5) ran: it deletes the demo S3 bucket, DynamoDB table, Lambda function and IAM role. Notebook 3's SQLite file (`inventory_demo.db`) is local and costs nothing.

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

**1. You ask an agent with no tools how many open issues your GitHub repo has. What do you get?**

- The exact count, from its training data
- Instructions for checking it yourself
- An error, because agents need tools to run
- A random number

> **Correct answer:** Instructions for checking it yourself
> Without tools the model can't reach GitHub, so the best it can do is tell you how to look it up. That's the gap tools close.

**2. Which three things turn a plain function into a Strands tool?**

- A class, a lock and async
- @tool, type hints and a docstring
- A REST API, JSON and a URL
- An MCP server, a client and a host

> **Correct answer:** @tool, type hints and a docstring
> The decorator registers it, the type hints define the inputs, and the docstring tells the model what it does and when to use it.

**3. What does the model actually see of your tool?**

- The whole function, including its body
- Only the return value
- The name, the description and the input schema
- Nothing until the tool has run once

> **Correct answer:** The name, the description and the input schema
> The body stays private. The model sees the spec built from the name, docstring and type hints, plus whatever result the tool returns.

**4. In the sales assistant, who decided to call get_sales_data, then analyze_sales, then send_email?**

- You, in an if/else block
- Strands, alphabetically
- The model, at run time, from the request and the tool descriptions
- The order of the tools list

> **Correct answer:** The model, at run time, from the request and the tool descriptions
> Nobody scripted the order. The model chose each next step based on the request and each result.

**5. Why prefer several focused tools over one mega-tool?**

- Python can't handle long functions
- They're easier for the agent to reason about, easier to maintain and reusable elsewhere
- Bedrock limits tool size
- Mega-tools can't have docstrings

> **Correct answer:** They're easier for the agent to reason about, easier to maintain and reusable elsewhere
> Single-purpose tools are like clearly labelled buttons: the model picks the right one, and you can reuse them in other agents.

**6. use_aws is about to call dynamodb.update_item. What happens by default?**

- It runs silently
- It asks you to confirm first, unless BYPASS_TOOL_CONSENT=true
- It refuses, because use_aws is read-only
- It converts the call to a Lambda invocation

> **Correct answer:** It asks you to confirm first, unless BYPASS_TOOL_CONSENT=true
> use_aws asks for confirmation before create, update and delete operations. Notebook 2 sets BYPASS_TOOL_CONSENT=true so the demo runs end to end.

**7. You're signed in as a read-only user and ask the agent to update a DynamoDB item. What happens?**

- use_aws escalates its own permissions
- The update succeeds because the agent asked nicely
- AWS returns AccessDenied: the agent can only do what your IAM permissions allow
- The agent creates a new table instead

> **Correct answer:** AWS returns AccessDenied: the agent can only do what your IAM permissions allow
> use_aws calls AWS with your credentials. IAM still decides what's allowed, which is exactly what you want.

**8. Your agent opens a new database connection on every tool call. The fix?**

- Make every tool async
- Group the related tools in a class that opens one connection and shares it
- Add more docstrings
- Switch to a bigger model

> **Correct answer:** Group the related tools in a class that opens one connection and shares it
> A class holds the shared connection in self.db, opened once in __init__ and reused by every tool method.

**9. Three independent warehouse APIs each take 2 seconds. As async tools called in one turn, roughly how long do the checks take?**

- 6 seconds
- 4 seconds
- About 2 seconds
- Under 100 ms

> **Correct answer:** About 2 seconds
> Concurrent calls take about as long as the slowest one, not the sum.

**10. Should a tool that adds two numbers locally be async?**

- Yes, everything should be async
- No: it does no slow I/O, so async adds complexity without any speed-up
- Yes, otherwise it can't be a tool
- Only on Lambda

> **Correct answer:** No: it does no slow I/O, so async adds complexity without any speed-up
> Async helps when a tool waits on slow input/output. Pure, instant calculations gain nothing.

> **8 or more correct:** Great work, you're ready for Section 3.
> **Fewer than 8 correct:** Revisit the parts you missed, then try Section 3.

Score: 0 of 10 answered

> **Up next: Section 3, agent memory:**
> Your agents can act, but they forget everything between conversations. Next you'll fix that with short-term and long-term memory and context-management strategies, using Mem0 and Amazon Bedrock AgentCore Memory, and build a personalised agent that remembers a user's preferences across sessions. Folder: `section-03-agent-memory`.
