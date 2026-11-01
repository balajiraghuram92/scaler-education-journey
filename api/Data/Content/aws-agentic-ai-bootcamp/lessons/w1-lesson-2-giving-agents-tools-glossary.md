# Glossary

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 2. Course code is provided under the MIT License.

AWS service names, tool names and library versions change often. When something here differs from what you see, the current documentation wins.

- **Tool** — A function or service an agent can call to do something it can't do with words alone: fetch data, compute exactly, change a system.
- **Function calling (tool use)** — The model's ability to say "run this function with these arguments" instead of only writing text. The agent runs it and returns the result.
- **Decorator** — A line starting with @ placed above a Python function to add behaviour. @tool registers a function as an agent tool.
- **Type hints** — Annotations like server_url: str or -> dict that say what type a value should be. Strands turns them into the tool's input schema.
- **Docstring** — The text in triple quotes at the top of a function. For tools, it becomes the description the model reads to decide when to call it.
- **API** — Application programming interface: a defined way for one program to ask another to do something, usually over the network.
- **JSON** — A simple text format for structured data: {curly braces} for objects, [square brackets] for lists. Most APIs speak it.
- **REST API** — A common style of web API: send an HTTP request (GET, POST…) to a URL and get JSON back.
- **Timeout** — The longest you're willing to wait for a response. requests.get(…, timeout=5) gives up after 5 seconds instead of hanging forever.
- **HTTP status code** — A number a server returns with every response: 200 means OK, 404 not found, 500 server error.
- **Exception** — Python's way of signalling an error. try/except catches it so your code can respond instead of crashing.
- **Regex (regular expression)** — A pattern language for matching text, like PROD-\d+ to find product IDs. Precise but brittle: it only matches what you anticipated.
- **Intent classifier** — A model trained to map a sentence to a fixed label like CHECK_INVENTORY. Traditional chatbots need one; tool-using agents don't.
- **SymPy** — A Python library for symbolic maths: exact arithmetic, solving equations, derivatives and integrals. The calculator tool is built on it.
- **Environment variable** — A named setting that lives outside your code, like BEDROCK_MODEL_ID or BYPASS_TOOL_CONSENT. Programs read it at run time.
- **Deprecation** — A warning that a feature still works but will be removed or replaced in a future version.
- **boto3** — The official AWS SDK for Python. Every AWS call in this course, including the ones use_aws makes, goes through it.
- **IAM** — AWS Identity and Access Management: decides who can do what in your AWS account. An agent can never do more than the credentials it runs with.
- **Amazon S3** — AWS object storage: files (objects) kept in buckets, read and written over an API.
- **Amazon DynamoDB** — A fully managed AWS NoSQL database. Items are looked up by key, like customer_id = 12345.
- **AWS Lambda** — Run a function in the cloud without managing servers. You pay only while it runs.
- **CSV** — Comma-separated values: a plain-text table, one row per line, columns separated by commas.
- **MCP (Model Context Protocol)** — An open standard for exposing tools and data to AI apps. Any MCP server can be plugged into a Strands agent. Covered in Section 5.
- **Lock** — A guard that lets only one thread use a shared resource at a time, so two tool calls don't trample the same database connection.
- **Thread** — A separate line of execution inside one program. Strands can run several tool calls on different threads at once.
- **Parameterised query** — SQL with placeholders (?) whose values are passed separately. The database treats them as data, never as SQL code.
- **SQL injection** — An attack where text meant as data is run as SQL. Building queries with f-strings invites it; parameterised queries prevent it.
- **async** — Marks a Python function that can pause while waiting (for a network reply, say) so other work runs meanwhile.
- **await** — Inside an async function: "wait here for this result, and let other tasks run in the meantime".
- **Event loop** — The scheduler that runs async functions, switching to whichever one is ready whenever another is waiting.
- **Concurrency** — Several tasks making progress in overlapping time, for example three API calls all waiting at once.
- **CLI** — Command-line interface: a program you use by typing commands in a terminal, like aws, pip or strands.
- **pipx** — Installs a Python command-line app into its own isolated environment, so its libraries don't clash with your projects.
- **Knowledge base (Bedrock)** — A managed Amazon Bedrock store that indexes your documents for retrieval. Agent Builder can use one to keep tools between sessions.
- **Large language model (LLM)** — A model trained on huge amounts of text that understands and writes language. The agent's brain.
- **AI agent** — Software that uses an LLM to plan, call tools, look at results and keep working towards a goal.
