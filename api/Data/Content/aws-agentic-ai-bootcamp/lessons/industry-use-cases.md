# Industry use cases

## 6.12 Industry use cases

Here's how these patterns play out in four industries, each with different deployment requirements and integration challenges. Watch for the last line of each: the deployment fit.

#### Financial services: fraud detection at transaction speed

A bank's fraud system kept catching suspicious crypto transactions, but it flagged legitimate customers so often that *"Why can't I buy Bitcoin?"* became a daily support ticket. The fraud team was drowning in false positives while real fraudsters slipped through. The fraud model itself, a **SageMaker** endpoint trained on transaction patterns, was solid. The problem was context: it saw each transaction in isolation and didn't know the customer had been making similar purchases for months.

{{diagram:1}}

*Context first, then the model, then escalate only if needed.*

When a transaction arrives, the agent works sequentially: pull the customer's history from DynamoDB, feed that context to the SageMaker model alongside the current transaction, and escalate only when the risk score warrants it; high-risk transactions trigger a Lambda function that starts the investigation workflow. There's no hard-coded `if risk_score > 0.8: call_lambda()`: the agent reads the tool descriptions and orchestrates them based on the situation.

> **Deployment fit: AWS Lambda:**
> Each transaction is independent: no multi-turn conversation, no state between invocations. The agent processes one transaction, returns a decision and terminates. It scales to zero in quiet periods and to hundreds of concurrent invocations during market volatility.

#### Healthcare: multi-specialty surgical scheduling

Scheduling surgery means coordinating a surgeon, an anaesthesiologist, possibly a specialist, an available operating room, specific equipment that might be in use elsewhere, and a time the patient can actually make. A large hospital system did this manually: coordinators spent hours on the phone, checking calendars and leaving voicemails. By the time they found a slot, the patient had sometimes booked with a competitor.

{{diagram:2}}

*Sequential where it must be, parallel where it can be. Read the requirements first, then check every calendar at once.*

When a patient requests surgery, the agent checks the **Electronic Health Record** first: what kind of surgery, which specialists, which equipment. Then it queries multiple calendars *in parallel* to find a time when everyone is free. Once it finds a slot it books the appointments and sends SMS confirmations. It also checks equipment availability before booking and sends reminders at the right intervals, which it worked out from the tool descriptions and past scheduling patterns. You provide the tools; the model orchestrates them.

> **Deployment fit: AgentCore Runtime:**
> A scheduling conversation might run five messages before a procedure is confirmed, so this is a multi-turn workload. Each coordinator's conversation gets its own isolated session, and the idle timeout matches the natural pace of scheduling (a coordinator might step away to check something with a nurse). Your ECS lab runs this same scenario to teach always-on containers; with many coordinators needing private multi-turn sessions, Runtime is the better production fit.

#### Manufacturing: predictive maintenance on the factory floor

A factory had expensive CNC machines with bearings that failed without warning. One day a machine runs fine; the next it's down for three days waiting for parts. Each failure cost roughly $50,000 in lost production. Scheduled maintenance (replace bearings every six months regardless) was wasteful, and bearings still failed in between. Monitoring vibration sensors by hand produced too much data and too many false alarms.

{{diagram:3}}

*A legacy system becomes "just another tool". The ticketing system was built by another team years ago; an MCP server made it callable without custom integration code.*

The agent monitors vibration sensors continuously, analyses thermal images for heat patterns, and runs everything through a SageMaker model trained to predict bearing failures. When the risk score crosses a threshold, it checks parts inventory in the warehouse database and creates a maintenance ticket automatically. It also knows to check parts before scheduling maintenance and to schedule during low-production periods, which it learned from the tool descriptions and production schedules, not from hard-coded rules.

> **Deployment fit: Amazon ECS:**
> This is continuous monitoring, so it runs on ECS as a long-lived service. Lambda's 15-minute limit rules it out for an agent that never stops processing sensor data, and AgentCore Runtime's per-session isolation doesn't map well to a workload with no distinct user sessions.

#### E-commerce: customer support with specialised agents

An online retailer built one agent to handle all customer support: order tracking, product recommendations and returns. It confused return policies with shipping policies, recommended out-of-stock products, and knew a little about everything without knowing enough about anything.

{{diagram:4}}

*Agents as tools, from Section 4. Each specialist knows its own domain deeply; the orchestrator combines their answers.*

The fix was three specialised agents (Order Tracking, Product Expert, Returns) wrapped as tools that an orchestrator calls: the agents-as-tools pattern from Section 4. A customer asks about returning an order; the orchestrator calls Order Tracking to check shipment status, then Returns for the policy, and combines both into one reply. Each agent focuses on what it does best, and the orchestrator also uses sentiment analysis to spot frustrated customers who need a human.

> **Deployment fit: AgentCore Runtime:**
> Customer support is conversational and multi-turn. Each customer's conversation gets its own isolated session, so there's no cross-customer data leakage even though the agents share tools that touch the same product catalogue and order database.

| Use case | Workload shape | Fit |
| --- | --- | --- |
| Fraud detection | One independent decision per event, spiky volume | Lambda |
| Surgical scheduling | Multi-turn, one private conversation per coordinator | AgentCore Runtime |
| Predictive maintenance | Never stops, no user sessions | ECS |
| Customer support | Multi-turn, many customers, shared tools | AgentCore Runtime |

## 6.13 Recap and self-check

Your agents are off your laptop and running on AWS.

You saw what changes in production (reliability, security, scale, cost, debugging) and learned to choose a home for each agent: **Lambda** for event-driven, quick tasks; **ECS** for always-on services, continuous workloads and multi-agent teams in one container; **AgentCore** for managed infrastructure with session isolation, auth, policy and observability built in. You met AgentCore's composable architecture (Runtime, Gateway, Identity, Policy, Memory, Observability and Evaluations), each solving one production problem, together or on its own. You deployed agents three ways, turned a REST API into MCP tools, ran MCP and A2A in the cloud behind OAuth, and learned the patterns for connecting agents to databases, APIs and event-driven systems.

But *deployed* and *production-ready* aren't the same thing. Right now, if your agent starts hallucinating, you won't know until a user complains. If a retry loop runs away, you'll find out on the monthly bill. If someone discovers your endpoint, nothing stops them hammering it. That's Section 7.

{{diagram:5}}

*The section on one page. Three homes for the agent, plus two services you can add to any of them.*

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| What changes in production | Reliability, security, scale, cost and debugging all stop being optional |
| Lambda handler | Expensive, stateless setup at module level; a fresh agent per request; state in DynamoDB if you need it |
| Cold start | The extra seconds while a new execution environment starts and runs your setup code |
| Lambda limits | 15 minutes per invocation (29 s behind a default REST API), 250 MB zip vs 10 GB image |
| Bedrock IAM | Allow both the foundation-model ARNs and the inference-profile ARNs |
| ECS service, task definition, Fargate | The kitchen that keeps copies running, the recipe card, and servers you never see |
| Browser-carried history | Simple for demos; server-side sessions survive refreshes and can be audited |
| AgentCore | Composable managed services for the agent-specific layer: Runtime, Gateway, Identity, Policy, Memory, Observability, Evaluations |
| Runtime sessions | One microVM per session; Active, Idle, Terminated; 15-minute idle timeout; CPU not billed while waiting |
| `BedrockAgentCoreApp` | Four lines turn an agent into an HTTP service with `/invocations` and `/ping` |
| Gateway | OpenAPI, Lambda, Smithy or MCP targets become MCP tools; semantic search for big catalogues; separate inbound and outbound tokens |
| Identity | Validates inbound JWTs; keeps outbound OAuth tokens and API keys in a vault; user-delegated and machine-to-machine flows |
| Integration patterns | RDS Proxy, timeouts + backoff + circuit breakers, EventBridge + SQS + DLQ, sync vs async replies |

#### When something goes wrong

| What you see | What it usually means and how to fix it |
| --- | --- |
| `AccessDeniedException` when the deployed agent calls Bedrock | The role is missing a Bedrock resource (often the inference-profile ARN or the region-less foundation-model ARN), or the model isn't enabled in your account. Compare with the policies in `template.yaml` and `deploy.sh`. |
| Model not found / validation error on the model ID | The ID isn't exact. Copy it from Bedrock and pass it with `BEDROCK_MODEL_ID`. |
| Lambda lab returns `504` after about 29 seconds | The API Gateway REST API timeout. Send a shorter document, use a faster model, or move to a Function URL or AgentCore Runtime. |
| The first Lambda request takes 5–15 seconds | A cold start. Later requests on the same environment are faster. |
| `sam build` or `deploy.sh` fails straight away | Docker isn't running, the SAM CLI isn't installed, or credentials aren't set. On Windows, run the scripts from WSL or Git Bash. |
| ECS: "Need at least 2 public subnets" | Your default VPC's subnets don't route to an **internet gateway**. New accounts are fine; otherwise check the route tables. |
| ECS URL doesn't load | Wait 2–3 minutes for health checks. Check `aws logs tail /ecs/scheduling-agent`. If your public IP has changed since you deployed, the load balancer blocks you: its rule is only written on the first deploy, so run `./cleanup.sh` and deploy again, or add your new IP to the load balancer's security group. |
| AgentCore status `CREATE_FAILED` | Check the runtime's CloudWatch logs and that you may create IAM roles, ECR repositories and CodeBuild projects. |
| Session ID rejected | Runtime session IDs must be at least 33 characters; use a UUID, or two in a row. |
| Multi-agent: `401`/`403` after an hour | The Cognito token expired. Run `cognito_refresh_token`; the deployed agents also hold a copy (`AGENT_BEARER_TOKEN`), so redeploy them with the fresh token. |
| Gateway target creation fails right after creating the role | IAM changes take a few seconds to propagate. Wait and rerun the cell. |
| "Address already in use" running the multi-agent lab locally | Something else is on 8000, 9000 or 9001. Stop it, or stop old copies of the servers. |

#### Clean-up checklist

| Lab | Clean up with | What's left behind if you forget |
| --- | --- | --- |
| Lambda | `./cleanup.sh` | The function, API and image; idle Lambda costs little, but anyone who finds the URL can run up your Bedrock bill |
| ECS Fargate | `./cleanup.sh` | The running task and the load balancer, both billing every hour |
| AgentCore Runtime | Steps 8–9 of the notebook (`stop_runtime_session`, `runtime.destroy`) | The runtime and endpoint, open sessions until they time out, the image in ECR |
| AgentCore Gateway | Step 7 of the notebook | The gateway, credential provider, IAM role and S3 bucket |
| Multi-agent | `agentcore destroy` ×3 and `delete-user-pool` | Three runtimes, ECR images and the Cognito pool; log groups are kept until you delete them |

#### Self-check

**1.** In the Lambda lab, why is the model client created at module level but a new Agent created inside the handler?

- Agents can't be created at module level
- The model client is expensive and holds no conversation; the agent holds history, and a warm environment serves many different callers
- It makes cold starts disappear
- Lambda requires it

> **Answer:** The model client is expensive and holds no conversation; the agent holds history, and a warm environment serves many different callers. Share what's expensive and stateless; create per request what holds one caller's conversation.

**2.** The Lambda lab sits behind an API Gateway REST API. Roughly how long can a request take before it times out by default?

- 29 seconds
- 15 minutes
- 60 minutes
- 8 hours

> **Answer:** 29 seconds. Lambda itself allows 15 minutes, but the REST API in front of it times out at 29 seconds by default.

**3.** Your Lambda agent uses global.anthropic.claude-sonnet-4-6 and gets AccessDeniedException. What's most likely missing from the IAM policy?

- s3:GetObject
- ecs:RunTask
- Nothing; it must be a model ID typo
- The inference-profile ARN (and the region-less foundation-model ARN)

> **Answer:** The inference-profile ARN (and the region-less foundation-model ARN). IDs starting with us. or global. are inference profiles; IAM must allow the profile and the models behind it.

**4.** On ECS, what keeps two copies of your agent running and replaces one that crashes at 3 AM?

- The task definition
- The load balancer
- The ECS service
- CloudWatch

> **Answer:** The ECS service. The task definition is the recipe; the service keeps the desired number of tasks running and replaces failed ones.

**5.** In the ECS lab, how does the agent know "the 9 AM slot" refers to Dr. Arti's knee replacement?

- The browser sends the full history with each message and the server seeds a fresh agent with it
- The container remembers every user
- The load balancer keeps sessions
- AgentCore Memory

> **Answer:** The browser sends the full history with each message and the server seeds a fresh agent with it. The browser carries the history; production systems usually store it server-side instead.

**6.** A user takes a minute to reply between messages in an AgentCore Runtime session. What happens to CPU billing during that minute?

- You pay full CPU for the whole minute
- The session is terminated
- CPU isn't billed while the agent is just waiting
- The microVM is shared with another user meanwhile

> **Answer:** CPU isn't billed while the agent is just waiting. Runtime bills per second for resources actually consumed: CPU drops to zero while waiting, while memory is billed as long as the session is open and the state is kept.

**7.** What is the default idle timeout for an AgentCore Runtime session?

- 1 minute
- 15 minutes
- 60 minutes
- 8 hours

> **Answer:** 15 minutes. 15 minutes of inactivity, configurable; a session can live up to 8 hours in total by default.

**8.** What do the four BedrockAgentCoreApp lines add to a Strands agent?

- A Dockerfile
- A Cognito user pool
- An MCP server
- An HTTP server on port 8080 with POST /invocations and GET /ping

> **Answer:** An HTTP server on port 8080 with POST /invocations and GET /ping. The SDK provides the web server, the routes and the health check; your agent logic is unchanged.

**9.** Your gateway exposes 200 tools. How does the agent avoid loading all 200 definitions into every prompt?

- Use the gateway's semantic search tool, x_amz_bedrock_agentcore_search
- Split the agent into 200 agents
- Use a bigger model
- Delete 190 tools

> **Answer:** Use the gateway's semantic search tool, x_amz_bedrock_agentcore_search. The agent searches by meaning and loads only the few best matches; good API descriptions make the search accurate.

**10.** The agent must read a user's own Google Calendar on their behalf. Which flow does AgentCore Identity use?

- OAuth client credentials (machine to machine)
- A shared admin API key in an environment variable
- OAuth authorisation code grant: the user clicks Allow once and Identity stores and refreshes the tokens
- No authentication

> **Answer:** OAuth authorisation code grant: the user clicks Allow once and Identity stores and refreshes the tokens. User-delegated access needs the user's consent; client credentials are for the agent acting as itself on shared resources.

> **Scoring:** Great work, you're ready for Section 7. Revisit the parts you missed, then try Section 7.

Ten quick questions. Pick an answer to see why it's right or wrong.

Score: 0 of 10 answered

> **Up next: Section 7, evals, observability and governance:**
> Deployed isn't the same as production-ready. Next you'll find out how well your agent is doing (AgentCore Evaluations with a custom LLM-as-judge), what it's doing (tracing with OpenTelemetry into Jaeger, Langfuse, LangSmith and CloudWatch), and what it's allowed to do (Bedrock Guardrails for what it says, AgentCore Policy with Cedar for what it does). Folder: `section-07-evals-observability-governance`.
