# From laptop to production

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

An agent or your code Users, requests, clients Tools, healthy, allowed AWS infrastructure, AgentCore The model (Amazon Bedrock) Failures, limits, blocked

Section 6: Shipping agents to production

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 6 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### Shipping agents to production

Section 6. Everything so far has run on your laptop. Now you'll put agents behind real URLs on AWS three ways (a **Lambda** function, an always-on **ECS** container, and **AgentCore Runtime**), turn an existing REST API into agent tools with **AgentCore Gateway**, and learn the patterns for plugging agents into enterprise systems.

Folder `section-06-production-deployment` Labs `lambda` `ecs-fargate` `agentcore-runtime` `agentcore-gateway` `multi-agent-on-agentcore` Model: Claude Sonnet 4.6 on Amazon Bedrock

{{diagram:1}}

*One agent, three homes. The agent code barely changes; what changes is how it's woken up, how long it can run, what it remembers between requests, and how much of the plumbing you build yourself.*

## 6.0 From laptop to production

Over the last five sections you built agents that reason, use tools, remember conversations, work in teams and talk over MCP and A2A. All of it runs nicely on your laptop. Production is a different place.

The moment someone says *"let's put this in front of real users"*, questions appear that nobody asked during development. What happens when 200 people hit your agent at the same time? What happens when the model provider has a bad day? If the agent crashes at 3 AM and nobody notices until Monday, what then?

The AI part is rarely what slows teams down. It's the infrastructure: networking, **IAM** (Identity and Access Management) policies, containers, load balancers. A two-day deployment task becomes a week of troubleshooting because nobody on the team has deployed a **containerised** application before, and the error messages are hard to decode.

This section closes that gap. It won't turn you into a DevOps engineer, but it gives you enough to get agents running in production. For hardened deployments with custom networking, compliance requirements or multi-region failover, you'll still want to partner with your infrastructure team.

> **Think of it like this:**
> Cooking a great dish for your family is development. Opening a restaurant is production. The recipe is the same, but now you need a kitchen that's open on time every day, enough staff for the Friday rush, a fire extinguisher, a health inspection, a way to know when a dish went wrong, and a budget that doesn't burn the place down. This section is about the restaurant, not the recipe.

#### What you'll learn here

1. What actually changes when you move from development to production, and a readiness checklist
2. The four ways to run agents on AWS and how to choose
3. Deploying on AWS Lambda (serverless, event-driven) and on Amazon ECS with Fargate (always-on containers), with a lab for each
4. Amazon Bedrock AgentCore: its architecture, Runtime, Gateway and Identity, with three labs
5. Enterprise integration patterns for databases, APIs and events, and four industry use cases

#### Before you start

1. 1 A working Strands setup from earlier sections Plus basic Python functions and classes.
2. 2 An AWS account with permissions to create resources The labs create IAM roles, container registries, Lambda functions, ECS services, load balancers and AgentCore resources, and call Claude on Amazon Bedrock. Set `AWS_REGION=us-east-1` (or your Bedrock region).
3. 3 Docker, for the Lambda and ECS labs Familiarity with Docker helps but isn't required; this page explains what you need. The AgentCore labs don't need Docker on your machine.
4. 4 Command-line tools AWS CLI v2 for everything; the AWS SAM CLI for the Lambda lab; `pip install bedrock-agentcore-starter-toolkit` for the AgentCore labs; `jq` for the multi-agent lab. On Windows, run the shell scripts from WSL (recommended) or Git Bash.
5. 5 An IDE (optional) VS Code, Kiro, Claude Code or Cursor, and Jupyter for the two notebooks.

| Folder | Target | Example | On this page |
| --- | --- | --- | --- |
| `lambda/` | AWS Lambda behind API Gateway | Serverless contract-analysis agent | 6.3 |
| `ecs-fargate/` | Amazon ECS on Fargate behind a load balancer | Hospital surgical-scheduling agent with a chat UI | 6.4 |
| `agentcore-runtime/` | AgentCore Runtime | Contract-analysis agent deployed with the starter toolkit | 6.6 |
| `agentcore-gateway/` | AgentCore Gateway | A REST API (OpenAPI spec in S3) turned into MCP tools | 6.8 |
| `multi-agent-on-agentcore/` | AgentCore Runtime (MCP + A2A) | Finance orchestrator → stock agent (A2A) → stock tools (MCP) | 6.10 |
| `setup_cognito.sh` | Amazon Cognito | A user pool and OAuth token for the multi-agent deployment | 6.10 |

```bash title="terminal · quick start"
# AgentCore Runtime
cd agentcore-runtime && jupyter lab deploy_to_agentcore_runtime.ipynb

# ECS Fargate
cd ecs-fargate && chmod +x deploy.sh cleanup.sh && ./deploy.sh      # ./cleanup.sh when done

# Lambda
cd lambda && chmod +x deploy.sh cleanup.sh && ./deploy.sh           # ./cleanup.sh when done

# AgentCore Gateway
cd agentcore-gateway && jupyter lab gateway_openapi_target.ipynb

# Multi-agent (local first, then AgentCore) — see multi-agent-on-agentcore/README.md
```

> **These labs cost real money until you clean up:**
> Unlike earlier sections, these labs create AWS resources that keep running (and billing) after your script finishes: a load balancer bills by the hour whether anyone uses it or not. Every lab ends with a clean-up step. Run it the same day.

> **One model setting for every lab:**
> All agents default to `global.anthropic.claude-sonnet-4-6`. Set `BEDROCK_MODEL_ID` before deploying to change it; the deploy scripts and notebooks pass it through to the deployed agent.

## 6.1 What actually changes in production

A true-to-life story first. A team built a brilliant document analysis agent. It parsed PDFs, extracted key terms and summarised findings flawlessly in development. They demoed it to leadership on Thursday, got approval on Monday, and were in trouble by Wednesday.

The agent worked great for one document at a time. In production, 200 users hit it at once. Model calls started timing out. Temporary files piled up and filled the disk. One malformed PDF crashed the whole process, and there was no recovery: just silence. No logs, no alerts, nothing. They found out it was down when a VP called to complain.

{{diagram:2}}

*Same code, different world. Nothing in the agent's reasoning changed. What broke was everything around it: concurrency, resources, failure handling and visibility.*

This is a normal trajectory when you skip the production-readiness conversation. Here's what changes:

{{diagram:3}}

*Five habits that don't survive production. Each one has a production replacement; this section and the next show you how to put most of them in place.*

##### Reliability isn't optional

You need error handling, retries, **circuit breakers** and **graceful degradation**, so one failure doesn't take everything down.

##### Security becomes real

Proper secrets management, **least-privilege** IAM roles and network isolation replace the admin keys on your laptop.

##### Debugging gets harder

With many containers and interleaved requests you need structured logs, **distributed tracing** and observability. Section 7 covers this in depth; this section lays the groundwork.

#### Are you ready? Seven questions

Teams that rush to deploy often spend twice as long fixing things they should have handled up front. Before you go to production, answer these honestly. If most are missing, that's fine: this section and the next cover them.

Try it

##### Production readiness check

Ready

0 of 7

Readiness

Tick the ones you can honestly answer "yes" to.

- You've estimated what it will cost per month: *the pricing models compared (6.7) and each lab's cost notes*

## 6.2 Choosing a deployment path

Different agents need different homes. Here are two that look similar on paper and need completely different infrastructure.

{{diagram:4}}

*The workload picks the platform. Short, independent and spiky points one way; long-lived, stateful and always-on points the other.*

AWS gives you four options for running agents in production: **AWS Lambda**, **Amazon Elastic Container Service (ECS)**, **Amazon Elastic Kubernetes Service (EKS)** and **Amazon Bedrock AgentCore**. Each fits a different set of constraints. Picking the wrong one won't end your project, but it can cost you weeks of rework.

{{diagram:5}}

*A spectrum, not a ladder. More control means more to build and run yourself. None is "better"; each fits a shape of workload.*

> **Think of it like this:**
> **Lambda is a taxi:** you pay per ride, nothing is waiting between rides, and the driver forgets you when you get out. **ECS is a company car:** always parked outside and ready, but you pay for it all day and you maintain it. **AgentCore Runtime is a hotel room:** each guest gets a private room for their stay, housekeeping is included, and the room is wiped clean at checkout.

|  | Lambda | ECS Fargate | AgentCore Runtime |
| --- | --- | --- | --- |
| Shape | Function per request | Always-on web service | Managed agent runtime, one microVM per session |
| Max run time | 15 min (API Gateway: 29 s by default) | Unlimited | Up to 8 hours per session |
| You manage | Packaging | Containers, load balancer, scaling | Just the agent code |
| Good for | Short, bursty, event-driven tasks | Existing container platforms, custom web apps | Long-running, stateful, multi-user agents |

Let's explore each path, starting with the simplest.

## 6.3 AWS Lambda: serverless and event-driven

Back to the document analysis agent. A customer uploads a contract and the agent needs to process it. You don't want a server running 24/7 waiting for uploads that might come once an hour or once a minute. You want your code to run when a document arrives, process it, and stop.

**AWS Lambda** lets you attach code directly to an event. You write a **handler** function, connect it to a **trigger** (an S3 upload, an **API Gateway** request, a scheduled event), and Lambda runs it when the trigger fires. Nothing runs, and nothing is billed, in between. That's what **serverless** means: there are still servers, you just never see or manage them.

{{diagram:6}}

*Wake up, do the job, go back to sleep. The handler is the only entry point; triggers decide when it runs.*

#### The handler, from the course code

```python title="lambda/src/app.py · setup that runs once per environment"
import json
import os

from strands import Agent
from strands.models.bedrock import BedrockModel

MODEL_ID = os.environ.get("MODEL_ID") or os.environ.get("BEDROCK_MODEL_ID") or "global.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a document analysis assistant.
When given a contract or document, you:
1. Extract key terms and parties involved
2. Flag any risky or unusual clauses
3. Provide a clear summary

Be concise and specific. Cite the exact language from the document when flagging risks."""

# Initialize the model outside the handler so it is reused across warm invocations.
# The first request pays the setup cost; later requests on the same container reuse it.
model = BedrockModel(model_id=MODEL_ID)
```

Notice where `model` is created: **outside** the handler, at module level. Lambda doesn't start a fresh Python process for every request. While traffic is flowing it reuses the same **execution environment**, and module-level objects survive between calls. The first request pays the setup cost (importing Strands, creating the Bedrock client); every later request on that environment skips straight to the handler. Move that setup inside the handler and you pay it on every single call.

```python title="lambda/src/app.py · the handler, runs on every request"
def lambda_handler(event, context):
    """Handle API Gateway POST requests."""
    # Parse the request body
    if isinstance(event.get("body"), str):
        body = json.loads(event["body"])
    else:
        body = event.get("body") or event

    document_text = body.get("document_text", "")

    if not document_text:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'document_text' in request body"}),
        }

    # A fresh Agent per request: a warm container serves many different callers,
    # so conversation history must never carry over from one request to the next.
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, callback_handler=None)
    result = agent(f"Analyze this contract:\n\n{document_text}")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"analysis": str(result)}),
    }
```

1. 1 Parse the body API Gateway delivers the HTTP body as a JSON *string*; a direct test invocation might pass a dict. The code handles both.
2. 2 Validate input No `document_text`? Return a `400` with a clear error instead of sending an empty prompt to the model.
3. 3 A fresh `Agent` per request The model client is shared, but the agent is not. A warm environment serves many different callers, and an agent keeps its conversation in `agent.messages`. Reuse one agent and customer B's request would carry customer A's contract in its history. Expensive and stateless: share it. Cheap and stateful: create it per request.
4. 4 Return an HTTP response A `statusCode`, headers and a JSON body, which API Gateway turns into the HTTP reply.

{{diagram:7}}

*Pay the setup once per environment, not once per request. Anything at module level runs in INIT; anything inside the handler runs on every call.*

**Quiet weekend, provisioned environments kept:** Provisioned environments survived the weekend, so Monday's first requests are warm. The price: you paid for them all weekend while nobody used them.

**Quiet weekend, everything recycled:** Everything was recycled. Nothing ran and nothing was billed all weekend, but Monday's first customer gets a cold start.

Try it

##### Cold starts, warm starts and where your setup code lives

Model created outside the handler

Traffic spike: 3 at once

on Provisioned concurrency: keep 2 environments pre-warmed

Execution environments

Requests

0

Cold starts

0

Last setup delay

–

Idle environments you pay for

0

Send a request to see what happens. Setup delays here are illustrative (cold starts are typically a few seconds).

#### Packaging and deploying with SAM

The deployment uses an **AWS SAM** (Serverless Application Model) template: a YAML file where you define the Lambda function, the API Gateway trigger, the IAM permissions and the container configuration, then deploy it all with one command. SAM turns it into a **CloudFormation** stack, so everything is created, and later deleted, together.

```yaml title="lambda/template.yaml · settings and parameters"
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Strands document analysis agent on AWS Lambda behind API Gateway

Globals:
  Function:
    Timeout: 900
    MemorySize: 1024

Parameters:
  Architecture:
    Type: String
    Default: arm64
    AllowedValues:
      - arm64
      - x86_64
    Description: "Lambda architecture. Use arm64 for Apple Silicon / Graviton, x86_64 for Intel."
  ModelId:
    Type: String
    Default: global.anthropic.claude-sonnet-4-6
    Description: "Bedrock model or inference profile ID used by the agent."
```

`Timeout: 900` is Lambda's maximum (15 minutes) and `MemorySize: 1024` gives the function 1 GB (Lambda also scales CPU with memory). The two parameters let the deploy script choose the CPU architecture and the model without editing the template.

```yaml title="lambda/template.yaml · the function, its trigger, a bucket and the endpoint output"
Resources:
  DocumentAnalysisFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      Architectures:
        - !Ref Architecture
      Environment:
        Variables:
          MODEL_ID: !Ref ModelId
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - bedrock:InvokeModel
                - bedrock:InvokeModelWithResponseStream
              Resource:
                - "arn:aws:bedrock:*::foundation-model/*"
                - "arn:aws:bedrock:::foundation-model/*"
                - !Sub "arn:aws:bedrock:*:${AWS::AccountId}:inference-profile/*"
        - S3ReadPolicy:
            BucketName: !Ref DocumentBucket
      Events:
        AnalyzeContract:
          Type: Api
          Properties:
            Path: /analyze
            Method: post
    Metadata:
      DockerTag: v1
      DockerContext: ./src
      Dockerfile: Dockerfile

  DocumentBucket:
    Type: AWS::S3::Bucket

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/analyze/"
```

Two pieces are easy to get wrong and hard to debug when you do.

##### 1. The IAM policy needs more than one resource

| Resource ARN | Why it's there |
| --- | --- |
| `arn:aws:bedrock:*::foundation-model/*` | Calling a model directly, in any region |
| `arn:aws:bedrock:::foundation-model/*` | The region-less form used behind `global.` profiles, which can route a request to any region |
| `arn:aws:bedrock:*:${AWS::AccountId}:inference-profile/*` | The **inference profile** itself. IDs that start with `us.` or `global.` (like `global.anthropic.claude-sonnet-4-6`) are inference profiles, not models. |

> **The error won't tell you what's missing:**
> Leave out the inference-profile resource and you get an `AccessDeniedException` that doesn't clearly say which permission is missing. Include all of them from the start. Each **ARN** (Amazon Resource Name) is just AWS's unique address for a resource.

##### 2. Ship a container image, not a zip

{{diagram:8}}

*`PackageType: Image` tells SAM to build a Docker image from `src/Dockerfile` and Lambda runs it.*

```bash title="lambda/src/Dockerfile"
FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]
```

The base image is AWS's official Lambda Python image. `CMD ["app.lambda_handler"]` tells Lambda which function in which file is the handler. The model ID lives in an environment variable (`MODEL_ID`), so you can switch models by redeploying with a different parameter, without touching the code.

> **Model IDs must be exact:**
> Copy model IDs exactly as Bedrock lists them. Some include a version suffix (`global.anthropic.claude-haiku-4-5-20251001-v1:0`), others don't (`global.anthropic.claude-sonnet-4-6`). Drop or add a piece and you get a model-not-found style error that doesn't explain what's wrong.

#### The architecture

{{diagram:9}}

*The same agent-with-tools pattern, packed into one function. Tools are plain Python functions bundled in the package and run in-process. No queues, no orchestration layer, no sidecars: one function, one agent, one execution environment.*

A user sends a query through API Gateway, which invokes the Lambda function. Inside, your agent sits at the centre. It calls out to the LLM for reasoning and runs tools such as clause extraction or risk scoring. The lab agent has no custom tools at all; the model does the analysis, which keeps the example small.

#### Three things that will shape your design

##### 1. Statelessness

Each invocation is independent. If the agent asks a clarifying question and the customer replies, that reply is a *new* invocation, possibly on a different environment, and the agent doesn't remember the first one. Unless you persist the conversation somewhere and restore it, your users will complain the agent has amnesia. A common fix is **DynamoDB**: store the history keyed by a session ID, load it at the start of each invocation, save it at the end.

{{diagram:10}}

*The memory lives outside the function. Lambda environments come and go; the session record in DynamoDB doesn't.*

```python title="pattern sketch, not part of the labillustrative"
import json
import boto3
from strands import Agent

table = boto3.resource("dynamodb").Table("agent-sessions")
# model and SYSTEM_PROMPT are defined at module level, as in app.py

def lambda_handler(event, context):
    body = json.loads(event["body"])
    session_id = body["session_id"]

    # 1. Load this session's history (empty on the first turn)
    item = table.get_item(Key={"session_id": session_id}).get("Item", {})
    history = json.loads(item.get("messages", "[]"))

    # 2. Seed a fresh agent with it, then answer
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, messages=history)
    result = agent(body["message"])

    # 3. Save the updated history for the next invocation
    table.put_item(Item={"session_id": session_id, "messages": json.dumps(agent.messages)})
    return {"statusCode": 200, "body": json.dumps({"reply": str(result)})}
```

Keep an eye on size: a single DynamoDB item can hold at most 400 KB, and long conversations about long contracts can exceed it. Strands' built-in session managers (for example one that stores sessions in S3) are an alternative.

##### 2. Cold starts

Monday morning, nobody has used the agent since Friday. A customer uploads a contract and waits an extra few seconds (typically 2 to 5, and up to about 15 for a large container image like this lab's) while Lambda starts a fresh environment and loads your dependencies. That's a **cold start**. It happens on the first invocation and whenever Lambda scales out new environments during a spike. Container images make it slightly slower than zips. **Provisioned concurrency** keeps a set number of environments pre-warmed, but then you're paying for idle compute, which undercuts one of Lambda's main advantages. Try it in the simulation above.

##### 3. The execution ceiling

{{diagram:11}}

*Fifteen minutes is plenty, until it isn't. Most single-agent tasks fit easily; multi-agent workflows with retries and slow calls can hit the wall.*

A month in, a customer uploads a 200-page contract. The agent calls the model many times, cross-references clauses and builds a detailed report. Twelve minutes in, it's still going; at 15 minutes Lambda stops the invocation. **Lambda durable functions** (announced at re:Invent 2025) use checkpoint-and-replay: the function reruns from the start but skips completed checkpoints, resuming where it left off. That works, but it adds complexity to your design.

> **In the lab, the real limit is 29 seconds:**
> The lab puts Lambda behind an API Gateway REST API, which times out after **29 seconds** by default, long before Lambda's 15 minutes. Keep requests short, use a faster model (`global.anthropic.claude-haiku-4-5-20251001-v1:0`), or use a Lambda Function URL or AgentCore Runtime for long-running agents.

> **When Lambda fits:**
> Lambda works well when your agent responds to an event, does its work and finishes. If it needs to stay running, hold persistent connections, or coordinate a team of agents in a long process, you need something with more staying power. That's next.

#### Lab: a contract-analysis agent on Lambda

A serverless contract-analysis agent behind API Gateway: POST a document, get back key terms, flagged risks and a summary. `User → API Gateway → Lambda (container image) → Strands agent → Amazon Bedrock`.

1. 1 Check the prerequisites `aws sts get-caller-identity` (credentials), `sam --version` (SAM CLI) and `docker info` (Docker running).
2. 2 Deploy The script checks prerequisites, detects your CPU architecture (arm64 for Apple Silicon or Graviton, x86_64 otherwise), builds the image with `sam build` and deploys with `sam deploy`. It takes 2–3 minutes and prints your endpoint.
3. 3 Test with curl POST a contract to the endpoint. The first request is slower because of the cold start (5–15 seconds).
4. 4 Clean up the same day `./cleanup.sh` deletes the whole stack.

```bash title="lambda/deploy.sh · settings and architecture detection"
#!/bin/bash
set -e

STACK_NAME="document-analysis-agent"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-us-east-1}}"
MODEL_ID="${BEDROCK_MODEL_ID:-global.anthropic.claude-sonnet-4-6}"

# Auto-detect architecture: arm64 for Apple Silicon / Graviton, x86_64 for Intel
MACHINE_ARCH=$(uname -m)
if [ "$MACHINE_ARCH" = "arm64" ] || [ "$MACHINE_ARCH" = "aarch64" ]; then
  LAMBDA_ARCH="arm64"
else
  LAMBDA_ARCH="x86_64"
fi
```

```bash title="lambda/deploy.sh · build and deploy"
# --- Step 1: Build ---
echo "Step 1: Building container image (this takes 1-2 minutes the first time)..."
# Clean previous build artifacts to avoid cache issues
rm -rf .aws-sam 2>/dev/null || true
sam build
echo ""

# --- Step 2: Deploy ---
echo "Step 2: Deploying to AWS (this takes 2-3 minutes)..."
sam deploy \
  --stack-name $STACK_NAME \
  --resolve-s3 \
  --resolve-image-repos \
  --capabilities CAPABILITY_IAM \
  --region $REGION \
  --parameter-overrides Architecture=$LAMBDA_ARCH ModelId=$MODEL_ID \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset
```

`--resolve-s3` and `--resolve-image-repos` let SAM create the S3 bucket and container repository it needs; `CAPABILITY_IAM` allows it to create the IAM role; `--parameter-overrides` passes the detected architecture and your model into the template's parameters.

{{diagram:12}}

*One stack, one delete. Because everything belongs to one CloudFormation stack, `sam delete` in `cleanup.sh` removes it all. (Leave the S3 bucket empty: a bucket with files in it can't be deleted.)*

```bash title="terminal"
cd lambda
chmod +x deploy.sh cleanup.sh
./deploy.sh

curl -X POST <ApiEndpoint printed by deploy.sh> \
  -H "Content-Type: application/json" \
  -d '{"document_text": "This agreement is entered into by Party A and Party B. Party A shall deliver 1000 units by March 2027. Late delivery incurs unlimited liability."}'

./cleanup.sh      # when you're done
```

```text title="responseillustrative; the wording varies"
{"analysis": "**Parties:** Party A (supplier) and Party B (buyer).
**Key terms:** Party A must deliver 1,000 units by March 2027.
**Risky clause:** \"Late delivery incurs unlimited liability\" exposes Party A to
uncapped damages. Consider a liability cap or liquidated damages.
**Summary:** A simple supply agreement with one high-risk liability clause."}
```

> **The demo API has no authentication:**
> Anyone with the URL can call it and spend your Bedrock budget. Don't share the URL, and run `./cleanup.sh` the same day. For real use, add an API key and usage plan, IAM auth, or a Cognito authoriser.
