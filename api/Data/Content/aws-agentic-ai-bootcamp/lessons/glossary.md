# Glossary

## A–Z Glossary

Every underlined word on this page, in one place.

Revision notes for the Scaler AWS AI Bootcamp, based on the Day 1 practice code from Future with Shivank (AI Harness), sections 1 and 2.

Model names, library versions and free-tier limits change often. When something here differs from what you see, the current documentation wins.

- **API key** — A secret string that proves who you are to a service such as OpenAI or Tavily. Anyone holding it can spend your credits, so keep it out of code and screenshots.
- **.env file** — A plain text file of KEY=value lines kept next to your code but listed in .gitignore, so secrets never reach git. load_dotenv() reads it.
- **Environment variable** — A named value the operating system hands to every program it starts. SDKs read their keys from fixed names such as OPENAI_API_KEY.
- **uv** — A fast Python project tool. uv sync creates the virtual environment and installs the exact locked versions; uv run runs a command inside it.
- **Virtual environment** — A private folder of Python libraries for one project, so different projects don't clash over versions.
- **PromptTemplate** — A prompt with {placeholders} that LangChain fills in at run time, so the same instructions work on any input.
- **Placeholder** — A {name} in a template that gets replaced by real text when the chain runs. The keys you pass to invoke() must match.
- **Chat model** — A Python object that talks to an LLM, such as ChatOpenAI or ChatOllama. All of them share the same interface.
- **Runnable / RunnableSequence** — LangChain's common building block: anything you can .invoke(). Joining runnables with | makes a RunnableSequence.
- **LCEL** — LangChain Expression Language: building chains with the pipe operator, so the output of one block flows into the next.
- **Temperature** — A setting for how random the model's wording is. 0 asks for the most predictable answer.
- **Ollama** — A free app that downloads open-weights models and serves them on your own machine at localhost:11434. No key, no cost.
- **Open-weights model** — A model whose trained weights are published, so anyone can download and run it locally. Gemma, Qwen and Llama are examples.
- **AIMessage** — The object a chat model returns: the answer (.text), raw content, tool_calls, usage_metadata, response_metadata and an id.
- **Token** — The unit LLMs read and write: roughly three-quarters of an English word. Prices and limits are counted in tokens.
- **Responses API** — OpenAI's newer API. Its replies can be a list of content blocks, which is why .content may be a list and .text is safer.
- **LangSmith** — LangChain's tracing service. With LANGSMITH_TRACING=true and a key in .env, every run is recorded with no code changes.
- **Trace** — A recorded run showing each step, its inputs and outputs, latency, tokens and cost.
- **Tool** — A function an agent may call. The model sees only its name, input schema and description, and asks for it; the framework runs it.
- **Agent** — An LLM that decides which tools to call, in a loop, until it can answer. Agent = LLM + tools.
- **Agent loop** — Ask the model; if it requests a tool, run it and send back the result; repeat until it answers in plain text. Also called the ReAct loop.
- **Decorator** — A line starting with @ placed above a function to add behaviour. @tool turns a function into an agent tool.
- **Type hints** — Annotations like query: str that say what type a value should be. LangChain turns them into the tool's input schema.
- **Docstring** — The text in triple quotes at the top of a function. For a tool it's the description the model reads to decide when to call it.
- **HumanMessage** — A message typed by the user. An agent's input is a list of messages, starting with one of these.
- **ToolMessage** — The message LangChain adds after running a tool. It holds the tool's result, which the model reads next.
- **Tavily** — A web search API built for LLMs. Free tier: 1,000 credits a month. Its key must be named TAVILY_API_KEY.
- **SDK** — Software development kit: a vendor's library for calling its service from code, such as TavilyClient.
- **Integration** — A ready-made LangChain component published by a vendor, such as langchain_tavily.TavilySearch. Less code for you, kept up to date by them.
- **Structured output** — Making the model return data that matches a schema, instead of free text, so programs can use it without parsing.
- **Pydantic** — A Python library for describing data shapes as classes (BaseModel) and validating that data fits them.
- **JSON** — A simple text format for structured data: {curly braces} for objects, [square brackets] for lists. The common language of APIs.
