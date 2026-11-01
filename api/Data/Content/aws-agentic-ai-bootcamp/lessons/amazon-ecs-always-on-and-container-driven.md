# Amazon ECS: always-on and container-driven

## 6.4 Amazon ECS: always-on and container-driven

A nurse walks up to a scheduling terminal at 2 AM and types: *"Is Dr. Arti available Monday for a knee replacement?"* The agent checks the calendar and offers three open slots. The nurse replies: *"The 9 AM slot works, patient ID is P-1234."* The agent books it, confirms equipment for OR-3 and sends notifications.

Two messages, and the second only makes sense because the agent remembers the first. This isn't a one-off either: staff use the system around the clock, and a conversation might run three, four or five messages before a procedure is booked.

You *could* build this on Lambda: persist the conversation in DynamoDB, reload it on every invocation, rebuild the agent's context each time. It would work, but you'd be fighting the infrastructure instead of building the feature. A Lambda function wants to wake up, do a thing and go away. This agent needs to be awake, warmed up and ready at all times.

**Amazon ECS** (Elastic Container Service) gives you that. You put your agent in a **Docker container**, hand it to ECS and say "keep this running". Run it as an **ECS service** and it stays up. If the container crashes at 3 AM, the service notices and starts a new one. You don't get paged. You don't write recovery scripts.

> **What's a container?:**
> A container packs your code together with everything it needs to run (Python, libraries, settings) into one sealed image, like a shipping container that fits on any ship, train or truck. Build it once with `docker build` and it runs the same on your laptop and on AWS.

#### From Lambda handler to web server

The mental shift: **on Lambda, your agent is a function that gets called. On ECS, your agent is a web server that's always listening.**

{{diagram:1}}

*Called vs listening. The model client and any expensive setup are created once when the container starts and live for the life of the container.*

Here's the course's scheduling agent. It's a **FastAPI** web app with a Strands agent inside.

```python title="ecs-fargate/app/app.py · the app, model ID and instructions"
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

app = FastAPI(title="Hospital Scheduling Agent")

# Serve the web UI
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

MODEL_ID = os.environ.get("MODEL_ID") or os.environ.get("BEDROCK_MODEL_ID") or "global.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a hospital surgical scheduling coordinator. You help staff
find available time slots for procedures by checking provider availability,
equipment needs, and operating room schedules.

When a scheduling request comes in:
1. Identify the procedure type and required specialists
2. Check provider availability across calendars
3. Verify equipment availability for the requested time
4. Suggest the best available slots
5. Confirm the booking details

Be concise and professional. Present scheduling options clearly with dates,
times, and any constraints. If conflicts exist, explain them and offer alternatives."""
```

```python title="ecs-fargate/app/app.py · a mock tool"
# --- Mock tools (replace with real integrations in production) ---

@tool
def check_provider_availability(provider_name: str, date: str) -> dict:
    """Check a healthcare provider's calendar availability for a given date.

    Args:
        provider_name: Name of the doctor or specialist
        date: Date to check in YYYY-MM-DD format

    Returns:
        Dictionary with available time slots
    """
    # In production, this would query the EHR/calendar system
    return {
        "provider": provider_name,
        "date": date,
        "available_slots": ["09:00-10:00", "11:00-12:00", "14:00-15:30"],
        "notes": "No conflicts found"
    }
```

#### **See the other two mock tools** (`check_equipment_availability`, `book_procedure`)

```python title="ecs-fargate/app/app.py · equipment and booking tools"
@tool
def check_equipment_availability(equipment_type: str, date: str, time_slot: str) -> dict:
    """Check if specific medical equipment is available for a procedure.

    Args:
        equipment_type: Type of equipment needed (e.g., 'laparoscopic tower', 'C-arm')
        date: Date to check in YYYY-MM-DD format
        time_slot: Time slot to check (e.g., '09:00-10:00')

    Returns:
        Dictionary with equipment availability status
    """
    return {
        "equipment": equipment_type,
        "date": date,
        "time_slot": time_slot,
        "available": True,
        "location": "OR-3"
    }

@tool
def book_procedure(
    patient_id: str, procedure: str, provider_name: str,
    date: str, time_slot: str, operating_room: str
) -> dict:
    """Book a surgical procedure after confirming all resources are available.

    Args:
        patient_id: Patient identifier
        procedure: Name of the procedure
        provider_name: Lead surgeon or provider
        date: Scheduled date in YYYY-MM-DD format
        time_slot: Confirmed time slot
        operating_room: Assigned operating room

    Returns:
        Booking confirmation with reference number
    """
    return {
        "status": "confirmed",
        "booking_ref": "BK-2026-04821",
        "patient_id": patient_id,
        "procedure": procedure,
        "provider": provider_name,
        "date": date,
        "time": time_slot,
        "room": operating_room,
        "message": "Booking confirmed. SMS notification sent to patient and provider."
    }
```

The tools return fixed mock data (three slots, OR-3, booking reference `BK-2026-04821`). In production each would query the EHR, the calendar system and the booking system. The agent code wouldn't change.

```python title="ecs-fargate/app/app.py · shared model, request shape, fresh agent with history"
# Shared model instance (stateless, safe to reuse across requests)
model = BedrockModel(model_id=MODEL_ID)

AGENT_TOOLS = [check_provider_availability, check_equipment_availability, book_procedure]

class HistoryMessage(BaseModel):
    role: str
    content: str

class ScheduleRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = []

def build_agent_with_history(history: list[HistoryMessage]) -> Agent:
    """Create a fresh Agent seeded with prior conversation turns."""
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=AGENT_TOOLS,
    )
    # Seed the agent's message buffer with previous turns so it
    # remembers everything the user already said in this session.
    for msg in history:
        agent.messages.append({"role": msg.role, "content": [{"text": msg.content}]})
    return agent
```

```python title="ecs-fargate/app/app.py · the endpoints"
@app.get("/health")
def health_check():
    """Health check endpoint for the ALB."""
    return {"status": "healthy"}

@app.get("/")
def root():
    """Serve the web UI."""
    return FileResponse(str(STATIC_DIR / "index.html"))

# A plain (sync) endpoint: FastAPI runs it in a worker thread, so a slow
# agent call doesn't block other requests.
@app.post("/schedule")
def schedule(request: ScheduleRequest):
    """Send a scheduling request to the hospital agent."""
    if not request.message:
        raise HTTPException(status_code=400, detail="No message provided")

    try:
        agent = build_agent_with_history(request.history)
        response = agent(request.message)
        return PlainTextResponse(content=str(response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

1. 1 `GET /health` A tiny endpoint the load balancer and Docker call to check the container is alive. If it stops answering, the container is replaced.
2. 2 `GET /` Serves the chat page (`static/index.html`).
3. 3 `POST /schedule` Builds a fresh agent seeded with the conversation so far, asks it the new message and returns plain text. It's a plain (not `async`) function on purpose: FastAPI runs it in a worker thread, so one slow agent call doesn't block other users.

#### Who remembers the conversation?

Each request carries `request.history`: the full conversation so far. The **browser** keeps track of everything the user and agent have said and sends it all with every new message. The server seeds a fresh agent with that history before processing the latest message. That's how, when the nurse says "the 9 AM slot works", the agent still knows it's about Dr. Arti and a knee replacement.

```javascript title="ecs-fargate/app/static/index.html · the browser keeps the history"
// Conversation history sent with every request so the agent
// remembers what the user said in previous turns.
const history = [];
…
  try {
    const res = await fetch('/schedule', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: msg, history: history })
    });
    thinking.remove();
    if (res.ok) {
      const text = await res.text();
      addMsg(text, 'agent');
      // Append both turns so the next request carries full context
      history.push({ role: 'user', content: msg });
      history.push({ role: 'assistant', content: text });
      …
```

This is the simplest approach, not the only one. Strands has built-in session management that can persist conversations to the local filesystem or to Amazon S3, and you can write a custom session repository backed by DynamoDB or any database. Those are better for production because the *server* owns the state, so it survives page refreshes and can be audited. The browser-carries-history pattern suits demos and light deployments where you don't want a persistence layer.

Try it

##### The 2 AM booking, three ways

Browser sends history (the lab)

Send message 1, then message 2. Then try refreshing the browser between them.

#### What's actually happening on AWS

You don't need to be a networking expert to understand the ECS deployment model. Here's what it looks like:

{{diagram:2}}

*Browser → load balancer → container → model and tools. The load balancer is the front door; the ECS service keeps the containers behind it alive.*

A user opens a URL. That request hits an **Application Load Balancer**, which routes traffic only to healthy containers. Run two containers and one dies: the load balancer sends everything to the survivor while ECS starts a replacement. Users don't notice.

Behind it, the **ECS service** keeps your containers running. You tell it "I want two copies of my agent running at all times", and it makes that happen. Crash? Replaced. New version? The service rolls it out gradually, keeping the old version running until the new one passes its **health checks**.

The lab runs a single task (`DESIRED_COUNT=1`) to keep costs down, so a crash there means a short outage until ECS replaces it; raise the count to 2 or more when you need failover.

Each container runs from a **task definition**: a config file that says "use this Docker image, give it this much CPU and memory, send its logs to CloudWatch".

{{diagram:3}}

*Recipe, kitchen, dishes. The task definition describes one container; the service keeps the right number of them running inside a cluster.*

For the compute you have two options. With **AWS Fargate** you specify CPU and memory and AWS handles the servers: you never see an EC2 instance, never patch an operating system, never think about capacity. With the **EC2 launch type** you manage the underlying instances yourself, which you'd only do for something Fargate can't provide, like a GPU. Start with Fargate; switch later if you need to.

#### Lab: a hospital scheduling agent on ECS Fargate

A Strands agent served by FastAPI on ECS Fargate behind an Application Load Balancer, with a small chat UI. It isn't production-hardened (mock tools, no authentication, minimal error handling), but it walks through every step from Python code on your laptop to a running agent behind a public URL, and you can read the deploy script to understand each step.

```text title="architecture (from the lab README)"
Browser (chat UI) → ALB (port 80) → ECS Fargate task → Amazon Bedrock
                                       │
                                 FastAPI + Strands agent
                                 (tools: provider calendar,
                                  equipment check, booking)
```

##### Prerequisites

AWS credentials (`aws sts get-caller-identity`), Docker running (`docker info`), AWS CLI v2, and a default **VPC** with at least two public **subnets** (new accounts have one).

##### The container image

```bash title="ecs-fargate/Dockerfile"
FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

RUN useradd -m appuser
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

| Line | Why |
| --- | --- |
| `FROM …python:3.12-slim` | A small official Python base image (pulled from AWS's public registry to avoid Docker Hub rate limits) |
| `apt-get install curl` | Needed by the health check command |
| `pip install … then COPY app/` | Dependencies first, code second, so code changes don't reinstall every package |
| `useradd … USER appuser` | Don't run as root: if the app is ever compromised, the attacker isn't root in the container |
| `HEALTHCHECK … /health` | Docker checks the app every 30 seconds when you `docker run` it locally. ECS ignores this line and runs the identical check from the task definition (step 6), alongside the load balancer's own check. |
| `uvicorn … --workers 2` | **uvicorn**, the web server, runs two worker processes so requests are served in parallel |

##### Run it locally first (optional)

```bash title="terminal"
cd ecs-fargate
pip install -r requirements.txt
cd app && uvicorn app:app --port 8080
# open http://localhost:8080
```

##### What `deploy.sh` does, step by step

{{diagram:4}}

*Seven steps, all visible in one script. Every `aws` command in `deploy.sh` is something a platform team would otherwise do in the console.*

- **3. Creates two IAM roles:** Creates two **IAM roles**. The *execution role* (with AWS's managed policy) lets ECS pull the image and write logs. The *task role* gets only Bedrock invoke permissions; that's what your agent code runs as. Then it waits 10 seconds for IAM to propagate.

Click a step to see what it creates.

```bash title="ecs-fargate/deploy.sh · configuration"
# ── Configuration ──────────────────────────────────────────────────
APP_NAME="hospital-scheduling-agent"
CLUSTER_NAME="agent-cluster"
SERVICE_NAME="scheduling-agent-service"
TASK_FAMILY="scheduling-agent"
CONTAINER_PORT=8080
CPU=1024        # 1 vCPU
MEMORY=2048     # 2 GB
DESIRED_COUNT=1
MODEL_ID="${BEDROCK_MODEL_ID:-global.anthropic.claude-sonnet-4-6}"

REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null || true)}}"
REGION="${REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}"
IMAGE_TAG="latest"

# Who may reach the load balancer. Default: only your current public IP.
# For a live class demo you can open it to everyone: ALB_INGRESS_CIDR=0.0.0.0/0 ./deploy.sh
if [ -z "${ALB_INGRESS_CIDR:-}" ]; then
  MY_IP=$(curl -s --max-time 5 https://checkip.amazonaws.com | tr -d '[:space:]' || true)
  if [ -n "${MY_IP}" ]; then ALB_INGRESS_CIDR="${MY_IP}/32"; else ALB_INGRESS_CIDR="0.0.0.0/0"; fi
fi
```

```bash title="ecs-fargate/deploy.sh · step 6, the task definition"
# ── Step 6: Register task definition ──────────────────────────────
echo "Step 6/7: Registering task definition..."
TASK_DEF=$(cat <<EOF
{
  "family": "${TASK_FAMILY}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "${CPU}",
  "memory": "${MEMORY}",
  "executionRoleArn": "${EXEC_ROLE_ARN}",
  "taskRoleArn": "${TASK_ROLE_ARN}",
  "containerDefinitions": [
    {
      "name": "${APP_NAME}",
      "image": "${ECR_REPO}:${IMAGE_TAG}",
      "essential": true,
      "portMappings": [{"containerPort": ${CONTAINER_PORT}, "protocol": "tcp"}],
      "environment": [
        {"name": "MODEL_ID", "value": "${MODEL_ID}"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:${CONTAINER_PORT}/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${LOG_GROUP}",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "agent"
        }
      }
    }
  ]
}
EOF
)
echo "${TASK_DEF}" > /tmp/task-def.json
aws ecs register-task-definition --cli-input-json file:///tmp/task-def.json \
  --region "${REGION}" --output text --query 'taskDefinition.taskDefinitionArn'
rm /tmp/task-def.json
echo "  Task definition: ${TASK_FAMILY}"
```

`networkMode: awsvpc` gives each task its own network address (required for Fargate). There are two roles: the **execution role** is for ECS itself (pull the image from ECR, write logs), the **task role** is for your code (call Bedrock). Keeping them separate is **least privilege** in practice. `startPeriod: 60` gives the app a minute to boot before failed health checks count.

{{diagram:5}}

*Two locked doors. Only you can reach the load balancer, and only the load balancer can reach the container.*

The addresses use **CIDR notation**: `203.0.113.7/32` means exactly that one address, `0.0.0.0/0` means every address. The script writes the load balancer's rule only when it first *creates* the security group, so `ALB_INGRESS_CIDR` only takes effect on a first deploy. To change it later (or if your own IP changes), run `./cleanup.sh` and deploy again, or add a rule for your new IP to the load balancer's security group. Inside the load balancer, a **listener** on port 80 forwards requests to a **target group**: the set of containers, checked through `/health`.

```bash title="terminal · deploy, test, watch logs, clean up"
cd ecs-fargate
chmod +x deploy.sh cleanup.sh
./deploy.sh                                   # 3–4 min, then 2–3 min to pass health checks

# OR, on your first deploy, open the load balancer to everyone for a live class demo:
ALB_INGRESS_CIDR=0.0.0.0/0 ./deploy.sh

curl http://<ALB_DNS>/health
curl -X POST http://<ALB_DNS>/schedule -H 'Content-Type: application/json' \
  -d '{"message": "Schedule a knee arthroscopy for patient P-1234 with Dr. Smith on 2026-11-18"}'

aws logs tail /ecs/scheduling-agent --follow --region us-east-1

./cleanup.sh
```

Open the URL printed at the end and you'll see the chat UI. Type *"Is Dr. Smith available next Tuesday for a knee replacement?"*, then follow up with just a time slot and a patient ID. The agent connects the dots across messages. The point isn't the scheduling app; it's seeing the whole journey from Python on your laptop to an agent behind a public URL on AWS.

```text title="POST /scheduleillustrative; the wording varies"
I've checked Dr. Smith's calendar for 2026-11-18. Available slots:
  • 09:00–10:00   • 11:00–12:00   • 14:00–15:30
The arthroscopy tower is available in OR-3 for the 09:00 slot.
Shall I book patient P-1234 for 09:00–10:00 in OR-3?
```

> **Cost: clean up the same day:**
> About $0.05 per hour for one 1 vCPU / 2 GB task, plus the load balancer's hourly charge, whether or not anyone uses it. `./cleanup.sh` deletes the service, load balancer, target group, task definitions, cluster, ECR repository, log group, security groups and IAM roles. The README covers networking details, IAM and troubleshooting if you want to dig deeper.

#### When to reach for Amazon ECS

{{diagram:6}}

*Teams in one box, and setup paid once. These are the two situations where an always-on container clearly beats a function.*

**Multi-agent systems.** The e-commerce order-processing graph from Section 4 had specialised agents for risk, fraud, inventory, shipping and more. On ECS, all of them live in the same container and talk through plain function calls: no network hops, no serialisation overhead, no message queues between them. You deploy the whole team as one unit and scale by adding replicas.

**Expensive startup.** Database connection pools that take seconds to open, authenticated sessions with third-party APIs that involve OAuth token exchanges, ML models loaded into memory: on ECS that happens once and persists for the life of the container. On Lambda you'd pay some of it on every cold start, and all of it whenever Lambda scales up new environments during a spike.

## 6.5 Amazon Bedrock AgentCore

Deploying on Lambda and ECS meant writing Dockerfiles, configuring load balancers, creating IAM roles, adding health checks and managing task definitions. And those were the *simple* versions.

Productionising adds much more: monitoring, auto-scaling policies, certificates, **VPC** configuration and a dozen other things that have nothing to do with your agent's actual job. None of it is agent-specific: you'd do exactly the same for a REST API, a batch processor or a website. The infrastructure doesn't know or care that it's running an AI agent.

But agents have problems that generic compute doesn't solve for you:

{{diagram:7}}

*The part nobody warns you about. Generic infrastructure is well understood; the agent-specific layer on top is where teams lose weeks.*

This is where **Amazon Bedrock AgentCore** comes in. In Section 1 you met it in the middle layer of the AWS AI stack, the managed solutions alongside Amazon Bedrock, between ready-made applications above and do-it-yourself infrastructure below. In Section 3 you used AgentCore Memory for short- and long-term memory. Those were individual services solving individual problems. Now you'll see how the full set fits together.

#### The AgentCore architecture

AgentCore is a set of **composable services**, each solving a specific challenge every team hits when moving agents from prototype to production. Use them all together, or pick the ones you need.

{{diagram:8}}

*Every box solves a problem you'd otherwise build yourself. Understanding the architecture is what turns AgentCore from "another managed service" into a genuine shortcut to production.*

| Service | What it does | Covered |
| --- | --- | --- |
| **Runtime** | Where the agent actually runs. Framework-agnostic (Strands, LangGraph, CrewAI, LlamaIndex, OpenAI Agents SDK, Google ADK, Claude Agent SDK or your own) and model-agnostic (Bedrock, OpenAI, Anthropic, Google…). Can expose the agent over A2A so agents on other platforms can find and talk to it. | 6.6 |
| **Gateway** | Turns enterprise APIs (OpenAPI specs, **Smithy** models, Lambda functions, remote MCP servers) into MCP tools the agent can discover and call. No integration code per API. | 6.8 |
| **Browser** | A managed, sandboxed web browser the agent can use to interact with web pages | – |
| **Code Interpreter** | An isolated sandbox for running Python, JavaScript or TypeScript the agent writes. Browser and Code Interpreter show up as ordinary tools. | – |
| **Identity** | Authentication in both directions: users to your agent (Cognito, Okta, Entra ID, any OAuth provider), and your agent to external services on behalf of those users | 6.9 |
| **Policy** | Deterministic rules written in **Cedar** that intercept every tool call before it runs. "No refunds over $1,000" is enforced by the infrastructure, not the agent's reasoning, so no prompt can talk its way around it. | Section 7 |
| **Memory** | The short- and long-term memory service from Section 3, wired directly into Runtime | Section 3 |
| **Observability** | Captures reasoning steps, tool calls, model calls, policy decisions, latency and errors across every service. Built on **OpenTelemetry**, so it plugs into CloudWatch, Datadog, Grafana, Splunk and others. | Section 7 |
| **Evaluations** | **LLM-as-judge** scoring, built-in evaluators (faithfulness, relevance) and continuous online evaluation in production | Section 7 |

> **Think of it like this:**
> AgentCore is a serviced office building for agents. Runtime is the private office (one per visitor, cleaned after each meeting). Identity is the front desk checking badges. Policy is the building's rules that security enforces no matter what anyone says. Gateway is the switchboard that connects you to every department. Memory is the filing cabinet, Observability is the CCTV, and Evaluations is the performance review. Rent one office, or take the whole floor.

**The services are composable.** Run your agent on ECS but use Gateway for tools. Use Runtime for hosting but manage your own authentication. Use just Memory if that's all you need. Each service has its own API, so you can adopt them independently. Used together they're integrated: Identity flows through to Gateway, Runtime connects to Memory, and Observability captures the full picture without you instrumenting anything.

#### One request, end to end

Here's how the pieces work together. A user asks your agent: *"Analyse this sales data and create a summary report."* Step through it:

{{diagram:9}}

*The user sees a report with charts. Behind it, the AgentCore stack coordinates securely, with governance and full traceability. On Lambda or ECS you'd build most of this coordination yourself.*

Click step 1 to begin.

- **1. Authentication:** The request reaches AgentCore Identity, which validates the user's bearer token against their identity provider and creates the right session credentials. Nothing reaches your agent without this.
- **2. Agent processing:** The request lands on your agent in Runtime, in its own microVM. It checks Memory for context, including long-term insights like *this user prefers visual charts and usually asks for quarter-over-quarter comparisons*.
- **3. Tool discovery:** The agent asks Gateway: *I need tools for data analysis and report generation.* Gateway's semantic search returns the most relevant tools from the catalogue.
- **4. Policy evaluation:** Before any tool runs, Policy intercepts the call and checks it against Cedar rules: may this user query sales data only for their own region, or company-wide? Is the report limited to a department? May the agent call the export tool? Only if Policy permits does the call proceed.
- **5. Tool execution:** Gateway routes the authorised calls. The agent uses Code Interpreter to analyse the data in a sandbox and draw charts in the user's preferred style, and maybe Browser to pull market context from a web portal.
- **6. Memory update:** Short-term memory records the conversation. In the background, long-term extraction reinforces the chart preference, notes that this user often asks for sales analysis, and stores any new facts.
- **7. Observability and evaluation:** Throughout, Observability captured every step: authentication, memory retrieval, each tool call with parameters and results, each policy decision, each model call. Evaluations scores the interaction against your criteria (accurate? right steps? in scope?). Both land in the same trace.
