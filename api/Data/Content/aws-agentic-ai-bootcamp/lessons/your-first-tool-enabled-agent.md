# Your first tool-enabled agent

## 2.2 Your first tool-enabled agent

Let's build something you'd actually use: an agent that works out the tip and splits the bill when you're out for dinner with friends.

```pseudo title="01_building_tools.ipynb: tip calculator"
DEFINE calculate_tip(bill_amount, tip_percentage, num_people = 1)    // @tool; num_people is optional
    SET tip = bill_amount * (tip_percentage / 100)
    SET total = bill_amount + tip
    SET per_person = total / num_people
    RETURN a dict with bill, tip, total and per_person (last three rounded to 2 decimals)

CREATE agent = Agent(model, tools = [calculate_tip])
ASK agent: "The bill is $85. What's a 20% tip, and how much does each person pay if we're splitting it 4 ways?"
SAVE the answer in response
PRINT the text of the final answer
```

```python reveal title="01_building_tools.ipynb: tip calculator"
@tool
def calculate_tip(bill_amount: float, tip_percentage: float, num_people: int = 1) -> dict:
    """Calculate tip and split the bill among people.

    Args:
        bill_amount: Total bill amount in dollars
        tip_percentage: Tip percentage (e.g., 15, 18, 20)
        num_people: Number of people splitting the bill (default: 1)
    """
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    per_person = total / num_people

    return {
        "bill": bill_amount,
        "tip": round(tip, 2),
        "total": round(total, 2),
        "per_person": round(per_person, 2),
    }

agent = Agent(model=model, tools=[calculate_tip])

response = agent(
    "The bill is $85. What's a 20% tip, and how much does each person pay if we're splitting it 4 ways?"
)
print("\n\nFinal answer:\n", response.message["content"][0]["text"])
```

1. **Step 1: @tool def calculate_tip(…)** Create the tool: a normal Python function plus the three ingredients. `num_people: int = 1` has a default, so it's optional.
2. **Args: section** One line per parameter. This is how the model learns that "20%" means `tip_percentage=20`, not 0.2.
3. **return {…}** A dictionary is fine. The agent hands the whole thing back to the model, which turns it into a sentence.
4. **Step 2: Agent(model=model, tools=[calculate_tip])** Give the tool to the agent.
5. **Step 3: agent("…")** Ask in plain English. `response.message["content"][0]["text"]` is the text of the agent's final reply.

```text title="output (wording will vary)"
I'll calculate the 20% tip and split the bill among 4 people for you.
Tool #1: calculate_tip
Here's the breakdown:
- **Bill amount**: $85.00
- **20% tip**: $17.00
- **Total with tip**: $102.00
- **Amount per person** (splitting 4 ways): $25.50

So each person should pay $25.50.

Final answer:
 Here's the breakdown: …  So each person should pay $25.50.
```

**Splitting the bill.** Strands streams the agent's words live, and prints a `Tool #1: calculate_tip` line the moment it runs your tool. The last block is our own `print` of the final answer.

#### So what just happened?

1. 1 Understood the intent You were asking about a tip calculation.
2. 2 Extracted the numbers $85, 20%, 4 people.
3. 3 Called `calculate_tip` with them
4. 4 Got the result back
5. 5 Wrote a natural, helpful reply

{{diagram:1}}

*From a sentence to function arguments. The orange arrows are the model's work: reading loose English and filling in typed parameters. The rest is just your Python running.*

Here's what you *didn't* write:

- Logic to parse "The bill is $85" and pull out the number
- Code to recognise that "20%" means `tip_percentage=20`
- Rules to work out that "splitting it 4 ways" means `num_people=4`
- Any routing logic or if/else statements

The agent figured all of that out from what you described: the function name, its parameters and its docstring.

#### Try it yourself

Ask the same agent differently phrased questions. It understands intent, not just keywords:

```pseudo title="01_building_tools.ipynb"
ASK agent: "What's a 15% tip on $42?"
ASK agent: "Bill is $120, we want to tip 18%, split between 3 people"
ASK agent: "Calculate tip for $67.50 at 20%"
```

```python reveal title="01_building_tools.ipynb"
agent("What's a 15% tip on $42?")
agent("Bill is $120, we want to tip 18%, split between 3 people")
agent("Calculate tip for $67.50 at 20%")
```

Try it

##### Tip agent playground

Or type your own e.g. Dinner was $240, tip 10%, five of us

**Example prompts and the agent's answers:**
1. **The bill is $85. What's a 20% tip, and how much does each person pay if we're splitting it 4 ways?** Agent: A 20% tip on $85.00 is $17.00, making the total $102.00. Split 4 ways, each person pays $25.50.
2. **What's a 15% tip on $42?** Agent: A 15% tip on $42.00 is $6.30, making the total $48.30. (No split mentioned, so `num_people` used its default of 1.)
3. **Bill is $120, we want to tip 18%, split between 3 people** Agent: A 18% tip on $120.00 is $21.60, making the total $141.60. Split 3 ways, each person pays $47.20.
4. **Calculate tip for $67.50 at 20%** Agent: A 20% tip on $67.50 is $13.50, making the total $81.00. (No split mentioned, so `num_people` used its default of 1.)
5. **Dinner came to ₹1,700, add 10% and split it five ways** Agent: A 10% tip on ₹1,700.00 is ₹170.00, making the total ₹1,870.00. Split 5 ways, each person pays ₹374.00.

**If a value is missing:** The agent would ask a follow-up: "What was the bill amount?" (`bill_amount` is required, so the model asks rather than guesses.)
**If the tip is missing:** The agent would ask a follow-up: "What tip percentage would you like?" (`tip_percentage` is required, so the model asks rather than guesses.)

Tool call the model would make

Tool result (computed for real)

In the real agent the LLM does the extraction. Here a small pattern matcher stands in for it, so very unusual phrasings may trip it up; the model would cope.

#### The whole recipe, again

1. 1 Create a tool A Python function with `@tool`.
2. 2 Give it to an agent Add it to the `tools` list.
3. 3 Let the model decide when to use it

Whether the tool calculates tips or checks servers, the approach is identical; only the inside of the function changes. The agent needs to understand just three things about any tool, and it learns all three from your function's name, parameters and docstring:

{{diagram:2}}

*What, needs, returns. Write these three clearly and the agent will call your tool at the right moments with the right arguments.*

> **Think of it like this:**
> Splitting the bill at a dhaba: one friend says "₹1,700, add 10% for the waiter, five of us", and another opens the calculator app. The friend talking is the model (understands loose words), the calculator app is your tool (exact, boring, reliable), and whoever reads the result aloud is the agent.

## 2.3 The Strands tool ecosystem

You now know how to turn a Python function into a tool. The good news: you don't have to build every tool yourself.

When you start a software project, you don't write your own HTTP library or JSON parser; you install packages others built. Agent tools work the same way. Why spend three days building a web scraper when someone has already solved it? The agents in later sections reuse these same tools, just combined in more interesting ways.

> **Think of it like this:**
> Your phone's app store. You don't build a maps app or a UPI app before you can get anything done; you install them and get on with your day. The Strands toolbox is an app store for agent abilities: install once, then just import the tool you need.

Strands gives you tools from four places, and the agent treats them all the same way:

{{diagram:3}}

*Four pillars, one tools list. Start with built-in tools for common jobs, add custom tools for your business logic, and plug in MCP tools for specialised services.*

| Pillar | What it gives you | Where you use it |
| --- | --- | --- |
| Prebuilt community tools | The `strands-agents-tools` package: dozens of ready tools for files, shell commands, web search, HTTP requests, maths, AWS and more. Think of it as a package manager for agent abilities. | This section |
| Custom Python tools | When nothing prebuilt fits, such as your company's internal API or domain-specific logic, `@tool` turns any function into a tool. | 2.1, 2.2, 2.4, 2.5 |
| **MCP** tools | A whole ecosystem of standardised tools that work across agent frameworks. If someone has built an MCP server for a service (a database connector, an API wrapper), you plug it in without writing integration code. Public catalogues of MCP servers make them easy to find. | Section 5 |
| AWS service integrations | AWS-specific tools in the package (like `use_aws`), plus custom tools you write for S3, DynamoDB, Lambda, SageMaker, Bedrock and other services. Your agent gets direct access to your cloud infrastructure and data. | This section |

#### Prebuilt community tools

These tools handle common jobs out of the box: file operations, web searches, HTTP calls, AWS services, maths, even multi-agent orchestration. They're already installed with this section's `requirements.txt`; on their own you'd install them with:

```pseudo title="terminal"
RUN pip install strands-agents-tools   // add the community tools package
```

```bash reveal title="terminal"
pip install strands-agents-tools
```

Here's the prebuilt calculator in action. One import gives the agent expressions, equation solving and calculus:

```pseudo title="02_prebuilt_and_aws_tools.ipynb: calculator tool"
IMPORT Agent and calculator
CREATE agent = Agent(model, tools = [calculator], system_prompt = "You are a helpful math assistant.")
ASK agent: "What's 42 raised to the power of 9?"
ASK agent: "Solve the equation x^2 + 5x + 6 = 0"
ASK agent: "What's the derivative of sin(x) * cos(x)?"
```

> **Imported:**
> - `Agent` from `strands`: the class that runs the model together with its tools.
> - `calculator` from `strands_tools`: the prebuilt maths tool. It is built on SymPy, so it solves equations and does calculus exactly.

```python reveal title="02_prebuilt_and_aws_tools.ipynb: calculator tool"
from strands import Agent
from strands_tools import calculator

agent = Agent(model=model, tools=[calculator], system_prompt="You are a helpful math assistant.")

agent("What's 42 raised to the power of 9?")
agent("Solve the equation x^2 + 5x + 6 = 0")
agent("What's the derivative of sin(x) * cos(x)?")
```

| Question | What the calculator returns |
| --- | --- |
| 42 to the power of 9 | 406,671,383,849,472 (exact; an LLM guessing "in its head" often gets digits wrong) |
| x² + 5x + 6 = 0 | x = −2 or x = −3 |
| d/dx of sin(x)·cos(x) | cos²(x) − sin²(x), which simplifies to cos(2x) |

Under the hood the calculator uses **SymPy**, a symbolic maths library, so it handles complex expressions and calculus that would take real effort to implement yourself.

##### What's in the toolbox?

Think of these as categories of abilities you can add to an agent instantly:

| Category | Tools | What they do |
| --- | --- | --- |
| File operations | `file_read`, `file_write`, `editor` | Read and write files; advanced editing with syntax highlighting |
| Maths | `calculator` | Calculations, symbolic maths, equation solving |
| Web and search | `http_request`, `tavily_search`, `tavily_extract`, `exa_search`, `bright_data` | API calls, live web search, extracting page content, web scraping |
| Code execution | `python_repl`, `shell`, `code_interpreter` | Run Python, run shell commands, isolated sandbox execution |
| AWS services | `use_aws`, `retrieve`, `nova_reels`, `agent_core_memory` | Work with S3, DynamoDB, Lambda; query Bedrock Knowledge Bases; create videos; store memories |
| Memory and storage | `memory`, `mem0_memory`, `mongodb_memory`, `elasticsearch_memory` | Store and retrieve documents and memories across runs |
| Communication | `slack`, `speak` | Post to Slack workspaces; text-to-speech output |
| Image and video | `generate_image`, `image_reader`, `search_video`, `chat_video` | Create and analyse images; semantic video search |
| Automation and utilities | `browser`, `use_computer`, `cron`, `current_time`, `sleep`, `diagram`, `rss` | Web automation, desktop control, scheduling, time utilities, diagramming |
| Advanced | `swarm`, `workflow`, `use_llm`, `batch`, `mcp_client` | Multi-agent coordination, automated workflows, nested AI loops, parallel execution |

> **About those deprecation warnings:**
> In `strands-agents-tools` 0.8.x, `calculator`, `http_request`, `tavily` and `current_time` print a deprecation notice. They still work, and the course pins the version below 0.9 so they keep working. When you move on, their replacements are `http_request`/`web_fetch` from `strands.vended_tools`, the official Tavily MCP server, and `ContextInjector` for the current time.

Try it

##### Pick the right tools for the job

Toolbox: tap the tools this agent needs

**Tasks to match against the toolbox (tap a task, then tap the tools you'd give the agent):**
- **Task 1:** Fetch Bangalore's 7-day forecast, average the max temperatures, and save a summary file
- **Task 2:** Read last month's sales CSV from S3 and add up the revenue
- **Task 3:** Find today's top AI headline and post it to our team Slack
- **Task 4:** Run this Python snippet and tell me what it prints
- **Task 5:** Create a picture of a robot painting a sunset

**After choosing a task:** Now tap the tools you'd give this agent, then check.

**Feedback when you check:**
- **Spot on.** No missing or extra tools.
- **Missing:** the tool you needed (for example `http_request` or `tavily_search`).
- **Not needed:** the extra tool (harmless, but more for the model to choose from).
- **Works.** All needed tools are there, with extras.

**Why each task needs the tools it needs:**
> **Task 1:** http_request fetches the forecast, calculator averages it, file_write saves it. Exactly the chain notebook 2 runs.
> **Task 2:** use_aws reads the object from S3; calculator does exact addition.
> **Task 3:** A web tool (tavily_search, or http_request to a news API) finds the headline; slack posts it.
> **Task 4:** python_repl executes Python. shell would also run code, but it's broader and riskier than you need.
> **Task 5:** generate_image creates images with a Bedrock image model.

Pick a task first.

#### Many tools, one request

Give the agent several prebuilt tools and it works out how to use them together. Here it fetches a live weather forecast for Bangalore, crunches the numbers and saves a summary:

```pseudo title="02_prebuilt_and_aws_tools.ipynb: combining tools"
IMPORT file_write and http_request
SET environment variable BYPASS_TOOL_CONSENT = "true"   // skip the confirmation prompt (demo only)
CREATE agent = Agent(model, tools = [http_request, calculator, file_write], system_prompt = "You help with data analysis tasks.")
ASK agent: "Fetch the 7-day forecast for Bangalore, take the daily maximum temperatures,
            calculate their average, and save a short summary to weather_summary.txt"
```

> **Imported:**
> - `file_write` from `strands_tools`: the prebuilt tool that writes text to a file.
> - `http_request` from `strands_tools`: the prebuilt tool that makes web requests, here to fetch the forecast.

```python reveal title="02_prebuilt_and_aws_tools.ipynb: combining tools"
from strands_tools import file_write, http_request

os.environ["BYPASS_TOOL_CONSENT"] = "true"

agent = Agent(
    model=model,
    tools=[http_request, calculator, file_write],
    system_prompt="You help with data analysis tasks.",
)

agent("""
Fetch the 7-day forecast from
https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&daily=temperature_2m_max,temperature_2m_min&timezone=Asia/Kolkata
extract the daily maximum temperatures for Bangalore,
calculate the average maximum temperature over the period,
and save a short summary to weather_summary.txt
""")
```

```pseudo title="02_prebuilt_and_aws_tools.ipynb: check the file"
IF the file weather_summary.txt exists THEN
    PRINT the contents of weather_summary.txt
ELSE
    PRINT a note: no summary yet, scroll up to see which tools the agent called
```

```python reveal title="02_prebuilt_and_aws_tools.ipynb: check the file"
if os.path.exists("weather_summary.txt"):
    print(open("weather_summary.txt").read())
else:
    print("No weather_summary.txt yet — scroll up to see which tools the agent called.")
```

{{diagram:4}}

*Fetch, compute, save. You gave one paragraph of English. The agent chose the order (http_request, then calculator, then file_write) and passed each result to the next tool.*

> **New word: tool consent:**
> Tools that change things on your machine, like `file_write`, normally stop and ask you to confirm first. Setting the **environment variable** `BYPASS_TOOL_CONSENT=true` skips that prompt so the demo runs end to end. It's like turning off the OTP step for payments: fine in a sandbox, never in a real application.

#### AWS integration with `use_aws`

Most real applications run in the cloud. Your data sits in S3 buckets, your records in DynamoDB or RDS, your business logic in Lambda functions. An agent that can't touch these is disconnected from your actual systems. The prebuilt `use_aws` tool fixes that: describe what you want in English, and the agent turns it into AWS API calls, made with **boto3**.

{{diagram:5}}

*One tool, every AWS service. The model picks the service, operation and parameters; `use_aws` makes the boto3 call. Two safety gates stay in place: a confirmation for changes, and your IAM permissions.*

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.1 list your S3 buckets"
IMPORT use_aws
CREATE aws_agent = Agent(model, tools = [use_aws, calculator], system_prompt = "You are an AWS assistant ... Use region REGION.")
ASK aws_agent: "List all S3 buckets in my account"
```

> **Imported:**
> - `use_aws` from `strands_tools`: the prebuilt AWS tool. It turns a plain-English request into a boto3 call, using your credentials.

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.1 list your S3 buckets"
from strands_tools import use_aws

aws_agent = Agent(
    model=model,
    tools=[use_aws, calculator],
    system_prompt=f"You are an AWS assistant that helps manage cloud resources. Use region {REGION}.",
)

aws_agent("List all S3 buckets in my account")
```

> **Think of it like this:**
> `use_aws` is a helper at a government office who knows every form by heart. You say "I want to renew my licence", and they fill in the right form for the right counter. But your ID card still decides which counters will serve you. That ID card is IAM: `use_aws` can only do what your credentials are allowed to do.

##### Three real scenarios, on resources the notebook creates for you

The scenarios need real resources to act on, so notebook 2 first creates small demo ones, each with a random suffix so nothing you already own is touched, and deletes them all at the end.

{{diagram:6}}

*Create, use, delete. Setup and clean-up use plain boto3 so they're predictable; only the middle part is the agent working in English.*

#### Show the setup cell (3.0) that creates the demo resources

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.0 create the demo resources"
IMPORT csv, io, json, time, zipfile, uuid, boto3
CREATE a boto3 session in REGION, with clients for STS, S3, DynamoDB, IAM and Lambda
SET account_id = the AWS account number from STS
SET suffix = 6 random characters   // unique names, so resources you already have are never touched
SET BUCKET, TABLE, ROLE_NAME and the function name, all built from suffix

// S3 bucket with a sales CSV
CREATE BUCKET in REGION
SAVE six monthly sales rows (month, region, revenue) as sales-2024.csv in BUCKET
PRINT "S3 bucket ready"

// DynamoDB table with one customer
CREATE TABLE with customer_id as its key, billed per request
WAIT until TABLE exists
SAVE customer 12345 (Asha Rao, asha@example.com) in TABLE
PRINT "DynamoDB table ready"

// Lambda function with its IAM role
CREATE ROLE_NAME, trusted by Lambda, with basic Lambda logging permissions
WAIT 10 seconds   // let IAM propagate
CREATE the order-processor Lambda function (Python 3.12), whose handler returns the order_id with status PROCESSED
WAIT until the function is active
PRINT "Lambda function ready"
```

> **Imported:**
> - `csv` Python standard library: writes the sales rows as CSV text.
> - `io` Python standard library: in-memory buffers for the CSV text and the zip file.
> - `json` Python standard library: turns the role's trust policy into JSON text.
> - `time` Python standard library: `time.sleep` pauses so IAM can finish.
> - `zipfile` Python standard library: packs the Lambda handler into a zip file.
> - `uuid` Python standard library: makes the random suffix for unique names.
> - `boto3` AWS SDK for Python, package `boto3`: creates the clients that call S3, DynamoDB, IAM and Lambda.

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.0 create the demo resources"
import csv
import io
import json
import time
import zipfile

import boto3

session = boto3.Session(region_name=REGION)
account_id = session.client("sts").get_caller_identity()["Account"]
s3 = session.client("s3")
dynamodb = session.client("dynamodb")
iam = session.client("iam")
lambda_client = session.client("lambda")

import uuid

suffix = uuid.uuid4().hex[:6]  # unique names, so we never touch resources you already have
BUCKET = f"agent-tools-demo-{account_id}-{REGION}-{suffix}"
TABLE = f"customers-{suffix}"
FUNCTION = f"order-processor-{suffix}"
ROLE_NAME = f"order-processor-demo-role-{suffix}"

# --- S3 bucket + CSV -------------------------------------------------------
if REGION == "us-east-1":
    s3.create_bucket(Bucket=BUCKET)
else:
    s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": REGION})

rows = [
    ("month", "region", "revenue"),
    ("2024-01", "North", 120000), ("2024-02", "North", 135000), ("2024-03", "North", 142000),
    ("2024-01", "South", 98000), ("2024-02", "South", 104000), ("2024-03", "South", 111000),
]
buf = io.StringIO()
csv.writer(buf).writerows(rows)
s3.put_object(Bucket=BUCKET, Key="sales-2024.csv", Body=buf.getvalue().encode())
print(f"S3 bucket ready: s3://{BUCKET}/sales-2024.csv")

# --- DynamoDB table + one customer -----------------------------------------
dynamodb.create_table(
    TableName=TABLE,
    KeySchema=[{"AttributeName": "customer_id", "KeyType": "HASH"}],
    AttributeDefinitions=[{"AttributeName": "customer_id", "AttributeType": "S"}],
    BillingMode="PAY_PER_REQUEST",
)
dynamodb.get_waiter("table_exists").wait(TableName=TABLE)
dynamodb.put_item(
    TableName=TABLE,
    Item={"customer_id": {"S": "12345"}, "name": {"S": "Asha Rao"}, "email": {"S": "asha@example.com"}},
)
print(f"DynamoDB table ready: {TABLE}")

# --- Lambda function ---------------------------------------------------------
trust = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}],
}
role_arn = iam.create_role(RoleName=ROLE_NAME, AssumeRolePolicyDocument=json.dumps(trust))["Role"]["Arn"]
iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
time.sleep(10)  # let IAM propagate

handler_code = '''
import json

def handler(event, context):
    order_id = event.get("order_id", "unknown")
    return {"order_id": order_id, "status": "PROCESSED", "message": f"Order {order_id} processed successfully"}
'''
zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf, "w") as z:
    z.writestr("lambda_function.py", handler_code)

lambda_client.create_function(
    FunctionName=FUNCTION,
    Runtime="python3.12",
    Role=role_arn,
    Handler="lambda_function.handler",
    Code={"ZipFile": zip_buf.getvalue()},
    Timeout=10,
)
lambda_client.get_waiter("function_active_v2").wait(FunctionName=FUNCTION)
print(f"Lambda function ready: {FUNCTION}")
```

##### Data analysis on S3

Read a **CSV** from S3, total the revenue, and write a summary back.

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.2"
ASK aws_agent: "Read the sales data from the S3 bucket BUCKET, key sales-2024.csv,
    calculate the total revenue, and save a short summary back to the same bucket as sales-summary.txt"
```

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.2"
aws_agent(
    f"Read the sales data from S3 bucket '{BUCKET}' key 'sales-2024.csv', "
    "calculate the total revenue, and save a short summary back to the same bucket as 'sales-summary.txt'"
)
```

The six rows add up to **710,000** (North 397,000 + South 313,000). Expect the agent to read the file with S3 `get_object`, total it with the calculator, then write `sales-summary.txt` with `put_object`.

##### Customer service on DynamoDB

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.3"
ASK aws_agent: "Look up customer ID 12345 in the DynamoDB table TABLE and update their email to newemail@example.com,
    then read the item back to confirm"
```

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.3"
aws_agent(
    f"Look up customer ID 12345 in the DynamoDB table '{TABLE}' and update their email to newemail@example.com. "
    "Then read the item back to confirm."
)
```

##### Workflow orchestration with Lambda

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.4"
ASK aws_agent: "Invoke the order-processor Lambda function with the payload order_id 67890, and tell me the result"
```

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.4"
aws_agent(f"Invoke the Lambda function '{FUNCTION}' with the payload {{\"order_id\": \"67890\"}} and tell me the result")
```

Try it

##### See the AWS calls behind each English request

**Request:** List all S3 buckets in my account
- **use_aws:** `s3.list_buckets()`
- **Result:** 3 buckets, including agent-tools-demo-…-a1b2c3
- **Agent:** “You have 3 S3 buckets: … and agent-tools-demo-…-a1b2c3.”

**Request:** Read sales-2024.csv from the demo bucket, total the revenue, save a summary back
- **use_aws:** `s3.get_object(Bucket='agent-tools-demo-…', Key='sales-2024.csv')`
- **Result:** 6 rows: North 120,000 / 135,000 / 142,000; South 98,000 / 104,000 / 111,000
- **calculator:** `calculator('120000+135000+142000+98000+104000+111000')`
- **Result:** 710000
- **use_aws:** `s3.put_object(Bucket='agent-tools-demo-…', Key='sales-summary.txt', Body='Total revenue: 710,000 …')` (a change: would ask for consent; the notebook bypasses it)
- **Restricted user:** AccessDeniedException: not authorized to perform `s3:PutObject`
- **Result:** Saved sales-summary.txt
- **Agent:** “Total revenue for Jan to Mar 2024 is 710,000 (North 397,000, South 313,000). I saved the summary as sales-summary.txt.”
- **Agent, restricted user:** “Total revenue is 710,000, but I don't have permission to write sales-summary.txt to the bucket.”

**Request:** Look up customer 12345 and update their email to newemail@example.com
- **use_aws:** `dynamodb.get_item(TableName='customers-a1b2c3', Key={'customer_id': {'S': '12345'}})`
- **Result:** Asha Rao, asha@example.com
- **use_aws:** `dynamodb.update_item(TableName='customers-a1b2c3', Key=…, UpdateExpression='SET email = :e', …)` (a change: would ask for consent; the notebook bypasses it)
- **Restricted user:** AccessDeniedException: not authorized to perform `dynamodb:UpdateItem`
- **Result:** Updated
- **use_aws:** `dynamodb.get_item(TableName='customers-a1b2c3', Key=…)`
- **Result:** Asha Rao, newemail@example.com
- **Agent:** “Done. Customer 12345 (Asha Rao) now has the email newemail@example.com; I read the record back to confirm.”
- **Agent, restricted user:** “I found Asha Rao (customer 12345), but I'm not allowed to update the record. Ask an admin for dynamodb:UpdateItem.”

**Request:** Invoke the order-processor Lambda with order 67890
- **use_aws:** `lambda.invoke(FunctionName='order-processor-a1b2c3', Payload='{"order_id": "67890"}')`
- **Restricted user:** AccessDeniedException: not authorized to perform `lambda:InvokeFunction`
- **Result:** {"order_id": "67890", "status": "PROCESSED", "message": "Order 67890 processed successfully"}
- **Agent:** “The function ran: order 67890 is PROCESSED.”
- **Agent, restricted user:** “I can't invoke that function with your current permissions.”

on Run as a restricted user (read-only: no PutObject, no UpdateItem, no InvokeFunction)

Look at those requests again. You described what you wanted (read this file, update this record, invoke this function) and the agent worked out the AWS API calls. You didn't write boto3 code, handle AWS responses, or even name the operation. The pattern is: **one tool (`use_aws`), many services, plain-English requests.**

> **The resources must exist, and must be cleaned up:**
> These requests only work because cell 3.0 created the bucket, CSV, table and function first. Run the clean-up cell when you're done:

```pseudo title="02_prebuilt_and_aws_tools.ipynb: 3.5 clean up"
// S3: delete all objects, then the bucket
FOR EACH obj in the objects of BUCKET
    DELETE obj from BUCKET
DELETE BUCKET
PRINT "Deleted bucket" + BUCKET

DELETE TABLE
PRINT "Deleted table" + TABLE

DELETE the order-processor Lambda function
DETACH the basic logging policy from ROLE_NAME
DELETE ROLE_NAME
PRINT "Deleted Lambda function and role"
```

```python reveal title="02_prebuilt_and_aws_tools.ipynb: 3.5 clean up"
# S3: delete all objects, then the bucket
for obj in s3.list_objects_v2(Bucket=BUCKET).get("Contents", []):
    s3.delete_object(Bucket=BUCKET, Key=obj["Key"])
s3.delete_bucket(Bucket=BUCKET)
print("Deleted bucket", BUCKET)

dynamodb.delete_table(TableName=TABLE)
print("Deleted table", TABLE)

lambda_client.delete_function(FunctionName=FUNCTION)
iam.detach_role_policy(RoleName=ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
iam.delete_role(RoleName=ROLE_NAME)
print("Deleted Lambda function and role")
```

You've now used community tools and AWS integrations. Next, the tools only you can build.
