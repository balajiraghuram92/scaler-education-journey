# From chain to agent

## 0.5 From chain to agent

A model on its own can only produce text. It doesn't know today's weather, this week's news or the current price of anything. An agent fixes that by pairing the model with tools it may call.

Think of it as **agent = LLM (the brain that decides) + tools (functions it may call)**. LangChain's `create_agent(model, tools)` builds the whole **agent loop** for you:

1. Send the question and the list of tools to the model.
2. If the model replies "please call tool X with arguments Y", run X(Y).
3. Send the tool's result back to the model and repeat, until it answers in plain text.

{{diagram:1}}

*The model never runs code. Step 2 is only a request. LangChain runs the function and stores the result as a ToolMessage; then the model reads it and decides what to do next.*

Press the button to follow one run.

- 1 · Your question goes to the model as a HumanMessage.
- 2 · The model replies with a tool call: search({'query': 'Bengaluru weather now'}).
- 3 · LangChain runs search() and sends back a ToolMessage with the result.
- 4 · No more tool calls, so the model writes the final answer. Done.

#### A tool is a function with a menu card

To focus purely on the mechanics, the first script's `search` tool is a placeholder: whatever you ask, it returns the same weather report for Bengaluru. In 0.7 we swap in real search and nothing else changes.

```pseudo title="01_agent_with_placeholder_tool.py (core)"
DEFINE search(query) as a tool   // the docstring tells the model when to use it
    PRINT "search tool called with" and query
    RETURN the fixed Bengaluru weather report

SET llm = ChatOpenAI with model OPENAI_MODEL
CREATE agent = create_agent with model llm and tools [search]
SET result = agent.invoke with messages [HumanMessage with QUESTION]
CALL print_agent_trace(result)
```

> **Imported:**
> - `create_agent` from `langchain.agents`: builds the whole agent loop in one line.
> - `tool` from `langchain.tools`: the decorator that turns `search` into a tool the agent can call.
> - `HumanMessage` from `langchain_core.messages`, package langchain-core: a message typed by the user.
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the cloud chat model that drives the agent.

```python reveal title="01_agent_with_placeholder_tool.py (core)"
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

@tool
def search(query: str) -> str:
    """Look up live information on the internet.

    Use this for anything that changes over time and that you cannot know
    from memory: today's weather, recent news, current prices, upcoming events.

    Args:
        query: What to look up, as a short search phrase.
    """
    print(f"🔎 search tool called with: {query}")
    return "Bengaluru right now: 24°C, light drizzle, humidity 78%"

llm = ChatOpenAI(model=OPENAI_MODEL)
agent = create_agent(model=llm, tools=[search])

result = agent.invoke({"messages": [HumanMessage(content=QUESTION)]})
print_agent_trace(result)
```

1. **@tool** This **decorator** turns an ordinary function into something an agent can call.
2. **search, query: str, -> str** The name and **type hints** become the tool's name and input schema: one text argument called `query`.
3. **The docstring** Becomes the tool's description. It's written for the *model*: say clearly when the tool helps. The model decides whether and how to call it from this alone.
4. **create_agent(model, tools)** Builds the loop in one line.
5. **{"messages": [HumanMessage(...)]}** An agent's input is a chat-shaped list of messages. **HumanMessage** means "typed by the user".
6. **result** A dict whose `"messages"` list is the whole conversation, tool calls included.

> **Think of it like this:**
> The model is a customer in a restaurant who can't enter the kitchen. `@tool` prints a menu card: the dish name, what you need to say when ordering, and when it's a good choice. The customer only ever *orders*; the kitchen (LangChain) cooks and brings the plate back.

> **Test a tool without an agent:**
> `search.invoke({"query": "anything at all"})` calls it directly. `search.name` is `"search"` and `search.description` is the docstring text the model sees.

## 0.6 Reading an agent run

`print(result)` dumps the run as one giant unreadable line. The helper `agent_trace_printer.py` prints the same information one message per line, so you can see the loop.

```text title="uv run python 01_agent_with_placeholder_tool.py"
🔎 search tool called with: Bengaluru weather now

The agent produced 4 messages:
  [0] HumanMessage : What's the weather like in Bengaluru right now?
  [1] AIMessage    : 🛠  tool call → search({'query': 'Bengaluru weather now'})
  [2] ToolMessage  : (search) Bengaluru right now: 24°C, light drizzle, humidity 78%
  [3] AIMessage    : It's about 24°C in Bengaluru right now, with light drizzle and 78% humidity — keep an umbrella handy!

FINAL ANSWER:
It's about 24°C in Bengaluru right now, with light drizzle and 78% humidity — keep an umbrella handy!
```

- [0]HumanMessage The question you asked.
- [1]AIMessage The model *decides* to call a tool. Its text is empty and its `tool_calls` list holds the request. Notice the model wrote the query "Bengaluru weather now" itself.
- [2]ToolMessage LangChain *ran* the tool and added the result.
- [3]AIMessage No tool calls this time, so it's the final answer.

```pseudo title="agent_trace_printer.py (core)"
DEFINE _one_line(text, limit = 160):
    SET flat = text with all whitespace squashed onto one line
    IF flat has at most limit characters THEN RETURN flat
    RETURN the first limit characters of flat, plus how many characters were cut

DEFINE print_agent_trace(result):
    SET messages = result["messages"]
    FOR EACH message, with its index:
        SET kind = the class name of message
        SET tool_calls = message.tool_calls, or an empty list
        IF tool_calls is not empty THEN
            FOR EACH call in tool_calls:
                PRINT index, kind, "tool call" and the call name with its arguments, cut to 120 characters
        ELSE IF kind is ToolMessage THEN
            PRINT index, kind, the tool name and the result, on one line
        ELSE
            PRINT index, kind and the message text, on one line
    PRINT the text of the last message   // the final answer
```

```python reveal title="agent_trace_printer.py (core)"
def _one_line(text: str, limit: int = 160) -> str:
    flat = " ".join(str(text).split())
    if len(flat) <= limit:
        return flat
    return f"{flat[:limit]} … (+{len(flat) - limit} chars)"

def print_agent_trace(result: dict) -> None:
    messages = result["messages"]
    for index, message in enumerate(messages):
        kind = type(message).__name__
        tool_calls = getattr(message, "tool_calls", None) or []
        if tool_calls:
            for call in tool_calls:
                print(f"  [{index}] {kind:<13}: 🛠  tool call → {call['name']}({_one_line(call['args'], 120)})")
        elif kind == "ToolMessage":
            print(f"  [{index}] {kind:<13}: ({message.name}) {_one_line(message.text)}")
        else:
            print(f"  [{index}] {kind:<13}: {_one_line(message.text)}")
    print(messages[-1].text)
```

1. **_one_line()** Squashes text onto one line and cuts it at 160 characters, so long search results don't flood the terminal.
2. **type(message).__name__** The class name: `HumanMessage`, `AIMessage` or `ToolMessage`.
3. **getattr(..., "tool_calls", None) or []** Only AI messages have `tool_calls`; this safely gives an empty list for the rest.
4. **for call in tool_calls** One AI message can request several tools at once, so each gets its own line with the same index.
5. **messages[-1].text** The final answer is simply the text of the last message.

## 0.7 Real search: your own Tavily tool

Same agent, same tool name, same docstring. The only change is the inside of `search`: instead of a hard-coded string it calls **Tavily**, a search API built for LLMs.

```pseudo title="02_agent_with_tavily_sdk_tool.py (core)"
LOAD TavilyClient from the tavily package
SET tavily = TavilyClient()   // reads TAVILY_API_KEY from the environment

DEFINE search(query) as a tool, with the same docstring as Script 01
    PRINT "search tool called with" and query
    RETURN the Tavily search results for query

SET question = the words typed after the script name, or DEFAULT_QUESTION if there are none
SET result = agent.invoke with the question as a HumanMessage
```

> **Imported:**
> - `TavilyClient` from `tavily`, package tavily-python: Tavily's search SDK. It finds its key in `TAVILY_API_KEY`.

```python reveal title="02_agent_with_tavily_sdk_tool.py (core)"
from tavily import TavilyClient

tavily = TavilyClient()          # reads TAVILY_API_KEY from the environment

@tool
def search(query: str) -> dict:
    """Look up live information on the internet.
    ... same docstring as Script 01 ...
    """
    print(f"🔎 search tool called with: {query}")
    return tavily.search(query=query)

question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
result = agent.invoke({"messages": [HumanMessage(content=question)]})
```

1. **TavilyClient()** The vendor's **SDK**. The variable must be named exactly `TAVILY_API_KEY`; the SDK looks it up itself.
2. **-> dict** Tavily returns JSON (query, results with title, URL, snippet and score). LangChain turns the dict into text for the model automatically.
3. **sys.argv[1:]** Any words typed after the script name become the question, so you can ask anything.

```pseudo title="terminal"
RUN uv run python 02_agent_with_tavily_sdk_tool.py   // no question typed: uses the default question
RUN uv run python 02_agent_with_tavily_sdk_tool.py "your question"   // the words after the script name become the question
```

```bash reveal title="terminal"
uv run python 02_agent_with_tavily_sdk_tool.py        # default: Bengaluru tech meetups
uv run python 02_agent_with_tavily_sdk_tool.py "What's the weather like in Bengaluru right now?"
```

The default question asks for three upcoming AI or developer meetups in Bengaluru with date, venue and link. Watch the trail: the model may call `search` **several times in parallel** with different queries, for example "upcoming AI meetups Bengaluru" and "developer meetups Bangalore this month", before it answers. Live results change every day.

> **Writing your own wrapper:**
> This is the "wrap a vendor SDK in your own `@tool`" pattern. You control exactly what the model sees, but the tool only offers what you wrote: here, a single `query` argument. Tip: `tavily.search(query=query, max_results=5)` trims the results.

## 0.8 The ready-made TavilySearch tool

Tavily also publishes an official LangChain **integration**. Using it deletes our custom function and gives the model a much richer menu card.

```pseudo title="03_agent_with_builtin_tavily_tool.py (core)"
LOAD TavilySearch from the langchain_tavily package
SET search_tool = TavilySearch()   // also reads TAVILY_API_KEY
CREATE agent = create_agent with model llm and tools [search_tool]
PRINT "Tool name the LLM sees:" and search_tool.name   // prints tavily_search
```

> **Imported:**
> - `TavilySearch` from `langchain_tavily`, package langchain-tavily: Tavily's ready-made search tool for LangChain.

```python reveal title="03_agent_with_builtin_tavily_tool.py (core)"
from langchain_tavily import TavilySearch

search_tool = TavilySearch()          # also reads TAVILY_API_KEY
agent = create_agent(model=llm, tools=[search_tool])

print(f"Tool name the LLM sees: {search_tool.name}")   # → tavily_search
```

```text title="sample trail (live results change)"
  [1] AIMessage    : 🛠  tool call → tavily_search({'query': 'upcoming AI developer meetups Bengaluru',
                                                     'time_range': 'month', 'topic': 'general'})
  [2] ToolMessage  : (tavily_search) {"query": "upcoming AI developer meetups Bengaluru", "results": [...
```

|  | Your own tool (0.7) | TavilySearch (0.8) |
| --- | --- | --- |
| Code you maintain | A function and docstring | One line |
| Tool name | `search` | `tavily_search` |
| Arguments the model may set | `query` only | `query`, `include_domains`, `exclude_domains`, `search_depth`, `time_range`, `topic`, `start_date`, `end_date` and more |
| When the vendor's API changes | You update it | The vendor updates it |

Notice the model chose `time_range='month'` and `topic='general'` on its own, because the vendor's description told it those options exist. Rule of thumb: **if a well-maintained integration exists, prefer it over writing your own wrapper.**

## 0.9 Structured output

Free text is great for people but painful for programs: which part of this paragraph is the link? With `response_format`, the agent must also return its answer as data that matches a schema you define.

```pseudo title="04_agent_with_structured_output.py (core)"
DEFINE class Source: a web page the answer is based on
    title: text, a short title such as the event name
    url: text, the full link, starting with https://

DEFINE class AgentAnswer: the agent's final reply
    answer: text, the answer in plain words
    sources: a list of Source, empty when nothing is cited

CREATE agent = create_agent with model llm, the TavilySearch tool and response_format AgentAnswer
SET result = agent.invoke with the question as a HumanMessage
SET structured = result["structured_response"]   // a validated AgentAnswer
FOR EACH source in structured.sources:
    PRINT source.title and source.url
```

> **Imported:**
> - `BaseModel` from `pydantic`: the base class that describes a data shape and checks it.
> - `Field` from `pydantic`: adds a description to a field, which the model reads as an instruction.

```python reveal title="04_agent_with_structured_output.py (core)"
from pydantic import BaseModel, Field

class Source(BaseModel):
    """A web page the answer is based on."""
    title: str = Field(description="Short title of the page, e.g. the event name")
    url: str = Field(description="Full link to the page, starting with https://")

class AgentAnswer(BaseModel):
    """The agent's final reply: a readable answer plus the pages it used."""
    answer: str = Field(description="The answer to the user's question, in plain text")
    sources: list[Source] = Field(default_factory=list,
                                  description="Every web page used to write the answer")

agent = create_agent(model=llm, tools=[TavilySearch()], response_format=AgentAnswer)

result = agent.invoke({"messages": [HumanMessage(content=QUESTION)]})
structured: AgentAnswer = result["structured_response"]
for source in structured.sources:
    print(source.title, source.url)
```

1. **BaseModel** A **Pydantic** class describes the shape of the data you want back, and validates it.
2. **Field(description=...)** Like tool docstrings, class docstrings and field descriptions are sent to the model. They're instructions.
3. **list[Source]** Schemas can nest: an answer holds a list of sources, each with a title and URL.
4. **default_factory=list** An empty list if the agent cites nothing, instead of an error.
5. **response_format=AgentAnswer** The only change compared with Script 03.
6. **result["structured_response"]** A new key holding a validated `AgentAnswer`. The usual `"messages"` trail is still there.

#### How LangChain enforces the schema

{{diagram:2}}

*LangChain picks the strategy for you. ProviderStrategy is used for providers with native structured output (OpenAI, Anthropic, xAI and others). ToolStrategy works with any tool-calling model. Force one with `ToolStrategy(AgentAnswer)` or `ProviderStrategy(AgentAnswer)` from `langchain.agents.structured_output`.*

```text title="sample output"
============================================================
STRUCTURED RESPONSE
============================================================
type: AgentAnswer
answer:
  Here are 3 upcoming meetups in Bengaluru:
  1) <meetup name> — <date> — <venue>
  ...
sources (3):
  - <meetup 1 title>
    https://www.meetup.com/...
```

> **Don't parse the last message yourself:**
> With ProviderStrategy the last AIMessage holds the answer as JSON text; with ToolStrategy the last message is a ToolMessage saying "Returning structured response: …". Either way, read `result["structured_response"]`. Now your code can loop over `.sources`, for example to show each meetup link as a button, with no parsing at all.

> **Optional variation:**
> Structured output works with any tool. Copy the `TavilyClient()` line and your own `search` function from Script 02 into this file and set `tools = [search]`.

## 0.10 When things go wrong

Most first-run errors are about keys, models or the local server. Find your message here.

| Problem | Fix |
| --- | --- |
| `OPENAI_API_KEY is missing` | You haven't created `.env`. Run `cp .env.example .env` and paste your key. |
| `AuthenticationError` / 401 | The key is wrong or revoked. Create a new one in the OpenAI dashboard. |
| `model ... does not exist` | Your account can't use the default model. Set `OPENAI_MODEL=` in `.env` to one it can. |
| Ollama `ConnectionError` | The Ollama app isn't running. Start it, or run `ollama serve`. |
| `model 'gemma3:270m' not found` | Run `ollama pull gemma3:270m`. |
| `MissingAPIKeyError` / Tavily 401 | `TAVILY_API_KEY` is missing or misspelled in `.env`. |
| The agent answers without searching | Make the tool docstring more explicit, or ask something that clearly needs fresh data. |
| Meetup results look old | Live search varies. Add a month to the question, for example "… in Bengaluru in November". |
| `KeyError: 'structured_response'` | You're running Script 03; only Script 04 sets `response_format`. |

Optional tidy-up for your code: `uv run black .` then `uv run isort .`

## 0.11 Recap and self-check

You've revised the two foundations every lesson builds on: a chain that turns a prompt into an answer, and an agent that loops over tool calls until it can answer.

Keys live in `.env` and reach the SDKs through environment variables. A chain is `prompt | llm`; swapping `ChatOpenAI` for `ChatOllama` changes one line. The answer comes back as an `AIMessage`: read `.text`, count cost in `usage_metadata`, and watch `tool_calls`. An agent adds tools described by their name, type hints and docstring; LangChain runs them, and the trail of Human, AI, Tool and AI messages shows every step. A vendor tool like `TavilySearch` offers the model richer options, and `response_format` turns the final answer into a validated Pydantic object.

#### From this revision to Lesson 1

| Idea | Here (LangChain) | In Lesson 1 (Strands on Bedrock) |
| --- | --- | --- |
| The model | `ChatOpenAI(model=...)` | `BedrockModel(model_id=...)` |
| Building an agent | `create_agent(model, tools)` | `Agent(model=model, tools=[...])` |
| Defining a tool | `@tool` + type hints + docstring | The same: Strands' `@tool` |
| Token usage | `response.usage_metadata` | `response.metrics.accumulated_usage` |
| The loop ends when | The AIMessage has no `tool_calls` | The stop reason is `end_turn` |

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

**1. Why do the scripts load keys with load_dotenv() from a .env file?**

- It makes the model answer faster
- Keys stay out of the code and out of git, and every SDK reads them from environment variables
- OpenAI refuses keys typed into code
- It encrypts the keys

> **Correct answer:** Keys stay out of the code and out of git, and every SDK reads them from environment variables
> .env is listed in .gitignore, and load_dotenv() copies each KEY=value line into the environment, where OpenAI, Tavily and LangSmith look for their keys.

**2. What does prompt | llm create?**

- A Python list of two objects
- A RunnableSequence: the filled prompt flows into the model
- A shell pipe between two processes
- A second copy of the template

> **Correct answer:** A RunnableSequence: the filled prompt flows into the model
> The pipe operator (LCEL) joins runnables. chain.invoke({...}) runs the template first, then the model.

**3. To move Script 02 from OpenAI to a local Ollama model, what changes?**

- The prompt template
- The chain and invoke() call
- Only the model object: ChatOpenAI becomes ChatOllama
- Everything, local models need a different library for chains

> **Correct answer:** Only the model object: ChatOpenAI becomes ChatOllama
> Every LangChain chat model has the same interface, so the prompt, the chain and invoke() stay identical.

**4. Why does every script print response.text instead of response.content?**

- content is always empty
- On newer OpenAI models content can be a list of content blocks; text is always one plain string
- text is faster to compute
- content holds the prompt, not the answer

> **Correct answer:** On newer OpenAI models content can be a list of content blocks; text is always one plain string
> Through the Responses API, .content may be a list. .text works the same for every provider.

**5. Where do you find how many tokens a call used?**

- response.id
- response.tool_calls
- response.usage_metadata
- response.type

> **Correct answer:** response.usage_metadata
> usage_metadata holds input, output and total tokens in a provider-independent shape. That's your cost.

**6. With @tool, what does the model actually see about your function?**

- The full source code
- Its name, type hints (input schema) and docstring (description)
- Only the return value
- Nothing until it's called

> **Correct answer:** Its name, type hints (input schema) and docstring (description)
> That 'menu card' is all the model knows, which is why the docstring is written for the model.

**7. In the agent loop, who runs the search function?**

- The LLM, on OpenAI's servers
- LangChain, after the model requests it in a tool call
- Tavily decides when to run it
- The user, by pressing Enter

> **Correct answer:** LangChain, after the model requests it in a tool call
> The model only requests a call. LangChain executes the function and adds a ToolMessage with the result.

**8. The placeholder run prints 4 messages. What's the order?**

- Human, Tool, AI, AI
- AI, Human, Tool, AI
- Human, AI (tool call), Tool, AI (answer)
- Human, AI, AI, Tool

> **Correct answer:** Human, AI (tool call), Tool, AI (answer)
> Question, the model's tool request, the tool's result, then the final answer with no tool calls.

**9. What's the main gain from swapping your own Tavily wrapper for TavilySearch()?**

- It's the only way to search the web
- Less code to maintain and a richer menu card: the model can set time_range, topic, include_domains and more
- It doesn't need an API key
- It always returns exactly three results

> **Correct answer:** Less code to maintain and a richer menu card: the model can set time_range, topic, include_domains and more
> The vendor-maintained tool documents extra arguments, and the model used them on its own (time_range='month').

**10. When does LangChain use ToolStrategy for response_format?**

- Always
- When the model has no native structured output: it adds an extra 'answer' tool whose arguments are the schema
- Only with Tavily tools
- When the schema has no fields

> **Correct answer:** When the model has no native structured output: it adds an extra 'answer' tool whose arguments are the schema
> Providers with native support (OpenAI, Anthropic, xAI) get ProviderStrategy. Either way you read result["structured_response"].

> **Score 8 or more of 10:** Great work, you're ready for Lesson 1.
>
> **Score under 8:** Revisit the parts you missed, then try Lesson 1.

Score: 0 of 10 answered

> **Up next: Lesson 1, your first AI agent:**
> Same ideas, now on AWS: why a plain LLM isn't enough, RAG, the AWS agentic stack, MCP and A2A, and a Hello World agent with the Strands Agents SDK on Amazon Bedrock. [Open Lesson 1](/chapter/aws-agentic-ai-bootcamp/w1-lesson-1-your-first-agent/why-a-plain-llm-isn-t-enough).
