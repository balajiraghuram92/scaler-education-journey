# AgentCore Runtime

## 6.6 AgentCore Runtime

Runtime is where the agent lives and executes. Its defining feature: each user session gets its own **microVM**.

Inside that dedicated environment the agent can keep state, hold database connections and build up context across many turns. When the session ends, the whole microVM is terminated and its memory sanitised. Nothing is shared between sessions, so nothing can leak between them. In financial services, for example, an agent processing one client's portfolio has zero chance of exposing it to another client's session.

{{diagram:1}}

*One microVM per session. A microVM is a tiny virtual machine that starts in a fraction of a second but has the hard isolation of a full VM.*

Consider a multi-turn conversation where a user asks the agent to analyse a financial document. The agent extracts data, stores intermediate results and writes temporary files. On Lambda all of that vanishes between invocations. On ECS it lives in a shared container. On AgentCore each user gets their own sandbox, and the agent can behave as if it's running on a dedicated machine.

#### Session states, and what you pay for

When a user sends a request, AgentCore creates a session and starts a microVM. The session moves through three states: **Active** while the agent is processing, **Idle** while it waits for the next user message, and **Terminated** when it ends. The default idle timeout is **15 minutes**: if the user goes quiet longer than that, the session ends and the microVM is cleaned up. A session can live for up to **8 hours** in total; both limits are configurable.

The cost model is what makes this attractive. Runtime bills per second for the CPU and memory your session actually consumes. While the agent is *waiting* (for the user, for the model's reply, for a tool), CPU usage drops to zero, so in a typical support conversation where the user takes a minute between messages you pay CPU for the 10–20 seconds of real processing per turn, not for the silence. Memory is billed for as long as the session stays open, idle time included, which is why you stop sessions you've finished with (or let the idle timeout do it). Your session state is kept throughout.

Try it

##### A session's life, and its compute bill

No session Active Idle Terminated

User thinks for 1 minute

User walks away for 20 minutes

Active (agent working) Idle (waiting, state kept) Terminated

Session clock

0 s

CPU-busy time

0 s

Share of time with CPU billed

–

An always-on container bills CPU for

0 s

Start by sending a message. Timings are illustrative.

**A minute of silence.** The session is Idle: the microVM and the conversation are kept, but the CPU isn't working, so CPU isn't billed (memory still is, while the session is open). Send another message and you're back in the same session.

#### How long can a session run?

{{diagram:2}}

*The pattern sets the ceiling. For long jobs the agent tells AgentCore it's busy, not idle, so the session isn't cleaned up mid-task.*

If your agent kicks off a long operation, it reports `HealthyBusy` on its health-check endpoint so AgentCore knows the session is working, not idle. The SDK's `app.add_async_task(...)` and `app.complete_async_task(...)` helpers manage that for you.

#### Making an agent Runtime-ready: four additions

```python title="agentcore-runtime/agent.py"
import os

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

app = BedrockAgentCoreApp()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")

@tool
def extract_clauses(text: str) -> dict:
    """Extract key clauses from contract text."""
    # In production this would use NLP or a specialised model.
    # For this example we return a structured placeholder.
    return {"clauses": ["termination", "liability", "indemnification"]}

model = BedrockModel(model_id=MODEL_ID)
agent = Agent(
    model=model,
    tools=[extract_clauses],
    system_prompt="You are a document analysis assistant. Extract and summarize key contract clauses.",
)

@app.entrypoint
def handle(payload):
    response = agent(payload.get("prompt"))
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()
```

{{diagram:3}}

*No server code to write. The SDK provides the web server, the routes and the health check.*

Only four things change from local development code: import `BedrockAgentCoreApp`, create the `app`, decorate your invocation function with `@app.entrypoint`, and call `app.run()`. Behind the scenes the app becomes an HTTP service with `/invocations` for requests and `/ping` for health checks. The agent logic (tools, system prompt, model) is the same code you've been writing since Section 2.

One subtle point: here the `agent` is created *once, at module level*, which on Lambda would mix up different callers' conversations. On Runtime it's exactly right, because every session gets its own microVM and therefore its own agent object. Within a session, follow-up messages reach the same agent, so it remembers the conversation.

```bash title="terminal · test locally"
pip install bedrock-agentcore strands-agents
python agent.py
# in another terminal
curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" \
  -d '{"prompt": "What are the key clauses in a standard NDA?"}'
```

```text title="responseillustrative; the wording varies"
"I'd be happy to help, but I'll need the actual contract text to extract its clauses.
If you're asking generally, the most common NDA clauses are:\n\n1. **Definition of
Confidential Information**\n2. **Obligations of the Receiving Party**\n3. **Permitted
Uses**\n4. **Exceptions** (public or independently developed information)\n5. **Term**
\n6. **Return or Destruction**\n7. **Remedies**\n8. **Governing Law**\n\nPaste an NDA
and I'll extract its actual key clauses."
```

#### Any framework, deployed the same way

Runtime is framework-agnostic. Strands, LangGraph, CrewAI, OpenAI Agents SDK, Google's Agent Development Kit (ADK), the Claude Agent SDK, or something custom: they all deploy the same way. That matters because most organisations end up with agents in several frameworks, through acquisitions, team preferences, or because different frameworks suit different problems.

Say your team builds agents with the Claude Agent SDK and already has a whole programming model: a `CLAUDE.md` with project context, a `skills/` folder of reusable capabilities, MCP servers wired to your tools, maybe sub-agents running jobs in parallel. You can deploy all of that as-is: wrap the entry point with `@app.entrypoint` and add `app.run()`. The SDK handles its own tool discovery, skill loading and sub-agent orchestration inside the microVM. Runtime doesn't know or care what's inside; it manages the session, the isolation and the scaling.

{{diagram:4}}

*Bring your whole programming model. Everything runs inside the microVM; Runtime manages the session around it.*

#### Lab: deploy the contract agent to AgentCore Runtime

The notebook `agentcore-runtime/deploy_to_agentcore_runtime.ipynb` walks the full lifecycle using the **AgentCore starter toolkit**'s `Runtime` class: configure, launch, invoke, manage sessions, clean up. The build runs in AWS **CodeBuild**, so you don't need Docker. You need IAM permissions to create IAM roles, ECR repositories, CodeBuild projects, S3 buckets and AgentCore runtimes.

{{diagram:5}}

*Five calls from code to cloud and back. The first launch takes a few minutes; later updates are faster because the toolkit reuses cached dependencies.*

##### Step 0 and 1: tooling and the agent

```python title="notebook · install the deployment tooling on your machine"
%pip install -q bedrock-agentcore-starter-toolkit 'bedrock-agentcore>=1.24.0' 'strands-agents>=1.60.0' boto3
```

The notebook then writes the same `agent.py` you saw above, and a `requirements.txt` listing what gets installed *inside* the deployed container:

```bash title="agentcore-runtime/requirements.txt"
# Packages installed INSIDE the deployed AgentCore container
bedrock-agentcore>=1.24.0,<2.0.0
strands-agents>=1.60.0,<2.0.0
```

Step 2 is the local test you just saw: `python agent.py` in a separate terminal, then `curl` to `/invocations`. Stop it with Ctrl+C when you're happy.

##### Step 3: configure

```python title="notebook · configure"
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Runtime

region = Session().region_name or "us-east-1"
print(f"Deploying to region: {region}")

runtime = Runtime()
runtime.configure(
    entrypoint="agent.py",
    requirements_file="requirements.txt",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    region=region,
    agent_name="doc_analysis_agent",
)
```

`configure` generates a Dockerfile from your code and saves the deployment settings. The two `auto_create_…` flags ask the toolkit to create an IAM execution role with the permissions your agent needs and an Amazon **ECR** repository; it does that when you launch.

##### Step 4 and 5: launch and wait

```python title="notebook · launch"
import os

# The deployed agent reads BEDROCK_MODEL_ID (see agent.py); pass your choice through
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")

launch_result = runtime.launch(auto_update_on_conflict=True, env_vars={"BEDROCK_MODEL_ID": MODEL_ID})

print(f"Agent ID:  {launch_result.agent_id}")
print(f"Agent ARN: {launch_result.agent_arn}")
print(f"ECR URI:   {launch_result.ecr_uri}")
```

`launch` builds the container image in CodeBuild (ARM64), pushes it to ECR and creates the Runtime endpoint. `env_vars` passes your model choice into the deployed container, and `auto_update_on_conflict=True` lets you rerun it to update an existing agent.

```python title="notebook · wait until READY"
import time

status = runtime.status().endpoint["status"]
print(f"Status: {status}")
while status not in ["READY", "CREATE_FAILED", "UPDATE_FAILED"]:
    time.sleep(10)
    status = runtime.status().endpoint["status"]
    print(f"Status: {status}")

print("\nEndpoint is ready." if status == "READY" else "\nDeployment failed — check the console / CloudWatch logs.")
```

##### Step 6 and 7: invoke it

```python title="notebook · invoke with the starter toolkit"
response = runtime.invoke(
    {"prompt": "Analyze this contract clause: The vendor shall be liable for direct damages only, excluding consequential, incidental, or punitive damages."}
)
print(response["response"][0] if response.get("response") else response)
```

```python title="notebook · invoke with boto3, as another service would"
import json
import uuid

import boto3

client = boto3.client("bedrock-agentcore", region_name=region)

response = client.invoke_agent_runtime(
    agentRuntimeArn=launch_result.agent_arn,
    runtimeSessionId=str(uuid.uuid4()),
    qualifier="DEFAULT",
    payload=json.dumps({"prompt": "Summarize the liability and indemnification clauses in this contract."}),
)

session_id = response.get("runtimeSessionId")
print(f"Session ID: {session_id}")

# The body is streamed in chunks
content = [chunk.decode("utf-8") for chunk in response.get("response", [])]
print(f"\nAgent response:\n{json.loads(''.join(content))}")
```

1. 1 `invoke_agent_runtime` How a Lambda function, an ECS service or **Step Functions** would call your agent in production, the same pattern as calling any other AWS service.
2. 2 `runtimeSessionId` Which session (and so which microVM) the request belongs to. Reuse the same ID for the next message to continue the conversation; a new ID starts a new isolated session. IDs must be at least 33 characters, which a UUID (36) satisfies.
3. 3 A streamed body The response arrives in chunks; the code joins and decodes them.

##### Step 8 and 9: stop the session, then clean up

```python title="notebook · stop the session"
if session_id:
    client.stop_runtime_session(
        agentRuntimeArn=launch_result.agent_arn,
        runtimeSessionId=session_id,
        qualifier="DEFAULT",
    )
    print(f"Session {session_id} stopped.")
```

Each session costs money (vCPU and memory) while it's open. When a conversation is done, stop the session explicitly, or rely on the idle timeout (15 minutes by default) to clean it up.

```python title="notebook · destroy everything"
result = runtime.destroy(delete_ecr_repo=True)
print("Removed:", *result.resources_removed, sep="\n  - ")
if result.errors:
    print("Errors:", result.errors)
```

> **Prefer the command line?:**
> The starter toolkit also installs an `agentcore` CLI. Add `--deployment-type container` to get the same container build as the notebook; without it, the CLI may choose direct code deployment instead.

```bash title="terminal"
pip install bedrock-agentcore-starter-toolkit
agentcore configure -e agent.py --deployment-type container --non-interactive
agentcore deploy
agentcore invoke '{"prompt": "Summarize the termination clause risks"}'
agentcore destroy
```

> **A notice you may see:**
> Recent versions of the starter toolkit's CLI print a yellow notice recommending AWS's newer AgentCore CLI (the npm package `@aws/agentcore`, which is also called `agentcore` but has different commands). The course code uses the Python toolkit, which still works; set `AGENTCORE_SUPPRESS_RECOMMENDATION=1` to hide the notice.

##### Three ways to get code into Runtime

| Option | How | When |
| --- | --- | --- |
| Container built for you | Hand over your source; the toolkit generates a Dockerfile and builds it in the cloud (this lab) | The easy default |
| Bring your own container | Push an image your CI/CD pipeline already builds. It must be **ARM64** (Graviton), so plan your builds for that. | You already have container pipelines |
| Direct code deployment | Upload your Python code as a package, with no container at all | Simple agents, fastest iteration |

#### **See the Dockerfile the toolkit generates** (kept in the folder for reference)

```bash title="agentcore-runtime/Dockerfile"
# Reference copy of the Dockerfile the AgentCore starter toolkit generates.
# `runtime.configure(...)` / `agentcore configure` regenerates this file, so
# you normally never edit it by hand. It is kept here so you can see what
# gets built: an ARM64 Python image, your requirements, the AWS OpenTelemetry
# distro for observability, a non-root user, and your agent as the entrypoint.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1

COPY requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

# AWS Distro for OpenTelemetry — sends traces to CloudWatch (AgentCore Observability)
RUN uv pip install aws-opentelemetry-distro

# Run as a non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

# 8080 = HTTP agents, 8000 = MCP servers, 9000 = A2A agents
EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

COPY . .

CMD ["opentelemetry-instrument", "python", "-m", "agent"]
```

An ARM64 Python image, your requirements, the AWS Distro for OpenTelemetry (which feeds AgentCore Observability), a non-root user, and the three ports AgentCore uses: 8080 for HTTP agents, 8000 for MCP servers, 9000 for A2A agents.

> **Try next:**
> Add a tool to `agent.py` and run the configure and launch steps again to update the deployment.

## 6.7 How Runtime compares to Lambda and ECS

You've now seen all three deployment paths. Here's how they stack up.

|  | Lambda | ECS (Fargate) | AgentCore Runtime |
| --- | --- | --- | --- |
| Session model | Stateless: each invocation is independent | Shared container across requests | Dedicated microVM per user session |
| State across turns | Persist externally (DynamoDB), reload every call | In memory within the container | Kept automatically in the microVM |
| Max execution | 15 minutes per invocation | No limit (the container stays running) | 15 min sync, 60 min streaming, 8 hours async |
| Scaling unit | Per request | Per container (task count) | Per session |
| Pricing model | Per invocation + duration | Per allocated vCPU/memory (always on) | Resources actually consumed; CPU stops billing while waiting |
| Auth, observability, policy | You build it | You build it | Managed services you configure |
| Infrastructure control | Moderate (VPC, layers, concurrency) | Full (networking, security groups, instance types) | Abstracted: less control, less to manage |

The last two rows are usually where the decision is made. Lambda and ECS are general-purpose compute: they'll run your agent, but auth, observability, tool integration and policy enforcement are your responsibility. AgentCore handles those as managed services, which saves weeks of engineering, but you give up fine control over things like network placement, security groups and GPU access. **ECS is the escape hatch** when you need that control.

Try it

##### Pick the home for each agent

- Summarise every invoice PDF uploaded to S3, about 20 seconds each, with traffic that comes and goes. **Answer: Lambda.** Short, independent and event-triggered: a Lambda function attached to the S3 upload event.
- A support agent where each customer chats over several turns and must never see another customer's data. **Answer: AgentCore Runtime.** Multi-turn and many users who must be isolated: one microVM per session on AgentCore Runtime.
- A team of six agents that call each other with plain function calls, plus a GPU for a local model. **Answer: ECS.** One container holds the whole team, and only ECS (with the EC2 launch type) gives you GPUs.
- Continuous monitoring of factory sensors that never stops and has no user sessions. **Answer: ECS.** A long-lived service on ECS. Lambda's 15 minutes rules it out, and Runtime's per-session model doesn't fit.
- Score each card transaction as it arrives: one independent decision, scaling to zero at night. **Answer: Lambda.** Each event is independent with no state: Lambda scales from zero to hundreds of concurrent invocations.
- A research agent that sometimes needs three hours for a report, and you'd rather not build auth and tracing yourself. **Answer: AgentCore Runtime.** Runtime allows asynchronous jobs of up to 8 hours and gives you Identity and Observability as managed services.

0 of 6 answered
