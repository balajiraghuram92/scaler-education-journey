# Lab: MCP + A2A on AgentCore

## 6.10 Lab: MCP + A2A on AgentCore

In Section 5 you ran MCP and A2A on your laptop. This lab puts both protocols into production: a finance orchestrator talks A2A to a stock agent, which gets live prices from an MCP server. All three run on AgentCore Runtime, protected by OAuth.

{{diagram:1}}

*A2A between the agents, MCP to the tools, OAuth at every door. Three separate runtimes, each in its own microVMs, each scaling on its own.*

| File | Protocol | Local port | What it does |
| --- | --- | --- | --- |
| `stock_mcp_server.py` | MCP | 8000 | `get_stock_price` tool backed by yfinance |
| `stock_a2a_agent.py` | A2A | 9001 | Agent with the MCP tools + `http_request` |
| `orchestrator.py` | A2A | 9000 | Agent that calls the Stock Agent through an `ask_stock_agent` tool |

> **Ports AgentCore expects:**
> On AgentCore Runtime, HTTP agents listen on **8080**, MCP servers on **8000** (path `/mcp`), and A2A agents on **9000**. Locally the stock agent uses 9001 so it doesn't clash with the orchestrator; inside the AgentCore container it switches to 9000.

#### The MCP server

```python title="multi-agent-on-agentcore/stock_mcp_server.py"
import yfinance as yf
from mcp.server.fastmcp import FastMCP

# stateless_http=True: every request is independent — required on AgentCore
mcp = FastMCP("StockTools", host="0.0.0.0", stateless_http=True)

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """Get the latest stock price for a given ticker symbol (e.g. AAPL, MSFT, AMZN)."""
    try:
        stock = yf.Ticker(ticker.strip().upper())
        info = stock.info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        name = info.get("shortName", ticker.upper())
        currency = info.get("currency", "USD")
        change = info.get("regularMarketChangePercent")

        if price is None:
            return f"Could not find price for '{ticker}'. Check the ticker symbol."

        result = f"{name} ({ticker.upper()}): {currency} {price:.2f}"
        if change is not None:
            direction = "▲" if change >= 0 else "▼"
            result += f" {direction} {abs(change):.2f}%"
        return result
    except Exception as e:
        return f"Error fetching {ticker}: {e}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

A FastMCP server like Section 5's, with two production details. It runs over **Streamable HTTP** instead of stdio, because on AgentCore it's a remote service, not a child process (FastMCP's defaults, port 8000 and path `/mcp`, are exactly what AgentCore expects). And `stateless_http=True` makes every request independent, which AgentCore requires: the platform itself manages the MCP session (it adds an `Mcp-Session-Id` header and routes on it), so the server mustn't keep its own per-connection state.

#### The Stock Agent (A2A server with MCP tools)

```python title="multi-agent-on-agentcore/stock_a2a_agent.py · settings from the environment"
logging.basicConfig(level=logging.INFO)

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
STOCK_MCP_URL = os.environ.get("STOCK_MCP_URL", "http://localhost:8000/mcp")
# Set automatically on AgentCore Runtime; used as the public URL in the agent card
RUNTIME_URL = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9001/")
# Bearer token for calling the MCP server when it is deployed behind OAuth
BEARER_TOKEN = os.environ.get("AGENT_BEARER_TOKEN")

# Locally this agent uses 9001 (the orchestrator has 9000). On AgentCore Runtime,
# A2A agents must listen on 9000 — the deploy command passes PORT=9000.
PORT = int(os.environ.get("PORT", "9000" if os.environ.get("DOCKER_CONTAINER") else "9001"))

MCP_HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"} if BEARER_TOKEN else None
```

Everything that differs between your laptop and AgentCore comes from environment variables: where the MCP server is, the agent's public URL, the bearer token for calling the protected MCP server, and the port. Same code, both places.

```python title="multi-agent-on-agentcore/stock_a2a_agent.py · MCP tools + agent"
# MCP client for the stock price tools. Passing it straight into tools=[...]
# lets the agent manage the connection for us.
mcp_client = MCPClient(lambda: streamablehttp_client(STOCK_MCP_URL, headers=MCP_HEADERS))

stock_agent = Agent(
    name="Stock Agent",
    description="Provides stock prices and financial information.",
    model=BedrockModel(model_id=MODEL_ID),
    system_prompt=(
        "You are a financial assistant. Use get_stock_price to look up current stock prices. "
        "Use http_request to fetch data from financial websites when needed. "
        "Always provide the ticker symbol, current price, and any relevant context."
    ),
    tools=[mcp_client, http_request],
    callback_handler=None,
)
```

The `MCPClient` passes the bearer token as an HTTP header, and it goes straight into `tools=[...]` next to `http_request` (from `strands_tools`), so the agent opens and closes the MCP connection itself.

```python title="multi-agent-on-agentcore/stock_a2a_agent.py · serve over A2A, with a /ping"
a2a_server = A2AServer(
    agent=stock_agent,
    http_url=RUNTIME_URL,
    serve_at_root=True,
    skills=SKILLS,
    version="1.0.0",
    enable_a2a_compliant_streaming=True,
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    print(f"Stock A2A Agent on http://0.0.0.0:{PORT} (MCP: {STOCK_MCP_URL})")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

1. 1 `http_url=RUNTIME_URL` The URL written into the agent card. A2A clients send messages to the URL in the card, so on AgentCore it must be the agent's public Runtime URL, not `127.0.0.1`.
2. 2 `serve_at_root=True` + `to_fastapi_app()` Turns the A2A server into a FastAPI app mounted at `/`, inside a bigger FastAPI app that also has the `/ping` health check AgentCore calls.
3. 3 `uvicorn.run(..., host="0.0.0.0", port=PORT)` Listen on all interfaces (required inside a container) on 9001 locally or 9000 on AgentCore.

#### **See the skills in the agent card**

```python title="multi-agent-on-agentcore/stock_a2a_agent.py · skills"
SKILLS = [
    AgentSkill(
        id="stock_lookup",
        name="Stock Price Lookup",
        description="Get latest stock prices and financial info for any publicly traded company.",
        tags=["stocks", "finance", "prices", "market"],
        examples=[
            "What is the current price of AAPL?",
            "How is AMZN doing today?",
            "Get me the stock price for MSFT and GOOGL",
        ],
    ),
]
```

#### The Finance Orchestrator (A2A client inside a tool)

```python title="multi-agent-on-agentcore/orchestrator.py · the remote agent as a tool"
def remote_stock_agent() -> A2AAgent:
    """A client for the remote Stock Agent (adds the bearer token when deployed)."""
    if BEARER_TOKEN:
        http = httpx.AsyncClient(headers={"Authorization": f"Bearer {BEARER_TOKEN}"}, timeout=300)
        return A2AAgent(STOCK_A2A_URL, client_config=ClientConfig(httpx_client=http))
    return A2AAgent(STOCK_A2A_URL, timeout=300)

@tool
def ask_stock_agent(question: str) -> str:
    """Ask the Stock Agent (a remote A2A agent) for current stock prices and market information.

    Args:
        question: A natural-language question, e.g. "What is the current price of NVDA?"
    """
    return str(remote_stock_agent()(question))

orchestrator = Agent(
    name="Finance Orchestrator",
    description="Provides financial advice by coordinating with the Stock agent.",
    model=BedrockModel(model_id=MODEL_ID),
    system_prompt=(
        "You are a financial advisor assistant. When users ask about stocks, "
        "investments, or market conditions, use ask_stock_agent to get current prices. "
        "Provide helpful analysis and context with the data. This is not financial advice."
    ),
    tools=[ask_stock_agent],
    callback_handler=None,
)
```

This is the "give the orchestrator an LLM" extension from Section 5's lab, done properly. Strands' `A2AAgent` is a client for a remote A2A agent: call it like a local agent and it fetches the card, sends the message and returns the answer. Wrapping it in an `@tool` lets the orchestrator's model decide *when* to ask the stock agent. When deployed, an `httpx` client adds the bearer token to every A2A request.

#### **See the rest of `orchestrator.py`** (imports, settings, skills, server)

```python title="multi-agent-on-agentcore/orchestrator.py · imports and settings"
import logging
import os

import httpx
import uvicorn
from a2a.client import ClientConfig
from a2a.types import AgentSkill
from fastapi import FastAPI
from strands import Agent, tool
from strands.agent.a2a_agent import A2AAgent
from strands.models.bedrock import BedrockModel
from strands.multiagent.a2a import A2AServer

logging.basicConfig(level=logging.INFO)

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
RUNTIME_URL = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9000/")
STOCK_A2A_URL = os.environ.get("STOCK_A2A_URL", "http://127.0.0.1:9001")
# Bearer token for calling the Stock Agent when it is deployed behind OAuth
BEARER_TOKEN = os.environ.get("AGENT_BEARER_TOKEN")
PORT = int(os.environ.get("PORT", "9000"))
```

```python title="multi-agent-on-agentcore/orchestrator.py · skills and server"
SKILLS = [
    AgentSkill(
        id="finance_advisor",
        name="Finance Advisor",
        description="Answers finance questions using real-time stock data.",
        tags=["finance", "stocks", "investing", "market"],
        examples=[
            "How are the FAANG stocks doing?",
            "Should I look at NVDA right now?",
            "Compare AAPL and MSFT prices",
        ],
    ),
]

a2a_server = A2AServer(
    agent=orchestrator,
    http_url=RUNTIME_URL,
    serve_at_root=True,
    skills=SKILLS,
    version="1.0.0",
    enable_a2a_compliant_streaming=True,
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    print(f"Finance Orchestrator on http://0.0.0.0:{PORT} (Stock Agent: {STOCK_A2A_URL})")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
```

#### Part 1: run everything locally

```bash title="terminal"
cd multi-agent-on-agentcore
pip install -r requirements.txt

python stock_mcp_server.py      # Terminal 1
python stock_a2a_agent.py       # Terminal 2
python orchestrator.py          # Terminal 3

# Terminal 4: talk to the orchestrator with a raw A2A JSON-RPC request
curl -s -X POST http://localhost:9000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", "id": "1", "method": "message/send",
    "params": {"message": {"role": "user",
      "parts": [{"kind": "text", "text": "How is NVDA stock doing today?"}],
      "messageId": "test-1"}}
  }' | jq -r '.result.artifacts[0].parts[0].text'
```

That's the same `message/send` you saw on the wire in Section 5; `jq` digs the answer out of `result.artifacts[0].parts[0].text`. Change the port to 9001 to talk to the stock agent directly.

```text title="answerillustrative; prices are live and the wording varies"
NVIDIA (NVDA) is trading at USD 1xx.xx, ▲ 1.85% today. The move follows …
Context: semiconductor stocks are up broadly this week. This is not financial advice.
```

#### Part 2: deploy all three to AgentCore Runtime

You need the starter toolkit CLI (`pip install bedrock-agentcore-starter-toolkit`; AWS also ships a separate Node.js `agentcore` CLI with different commands, and this lab uses the Python one) and `jq`. Follow the request path, then the commands.

{{diagram:2}}

*Three runtimes, one request. AgentCore checks the token at every door before any of your code runs.*

- **1. Get a token:** `setup_cognito.sh` logs your test user in to the Cognito user pool and exports the access token as `$BEARER_TOKEN`. It's valid for one hour.
- **2. Call the orchestrator:** Your `curl` sends an A2A `message/send` to the orchestrator's Runtime URL with `Authorization: Bearer …` and a session ID. AgentCore checks the JWT against Cognito's discovery URL and the allowed client *before* any of your code runs; a bad or expired token never reaches the agent.
- **3. Orchestrator calls the stock agent:** The orchestrator's model decides to use `ask_stock_agent`. Inside it, `A2AAgent` fetches the stock agent's card and sends an A2A message to its Runtime URL, adding the bearer token.
- **4. Stock agent calls the tool:** The stock agent's model calls `get_stock_price`, which reaches the MCP server's Runtime URL over Streamable HTTP, again with the bearer token in the header.
- **5. MCP server:** The MCP server (stateless, port 8000, `/mcp`) looks up the live price with yfinance.
- **6. Result:** The result flows back: MCP result → stock agent's answer (A2A task) → orchestrator adds context → A2A task with an artifact → your terminal.

2 Call + JWT check

Click step 1.

##### Step 1: a Cognito user pool for OAuth

```bash title="terminal · from the multi-agent-on-agentcore folder"
pip install bedrock-agentcore-starter-toolkit
export REGION=us-east-1
export COGNITO_USERNAME=testuser
export COGNITO_PASSWORD='YourPassword123!'
source ../setup_cognito.sh

export AUTH_CONFIG="{\"customJWTAuthorizer\":{\"discoveryUrl\":\"$DISCOVERY_URL\",\"allowedClients\":[\"$CLIENT_ID\"]}}"
```

```bash title="setup_cognito.sh · what it creates"
_cognito_setup() {
  if [ -z "$REGION" ] || [ -z "$COGNITO_USERNAME" ] || [ -z "$COGNITO_PASSWORD" ]; then
    echo "Error: set REGION, COGNITO_USERNAME and COGNITO_PASSWORD first." >&2
    return 1
  fi

  # User pool
  POOL_ID=$(aws cognito-idp create-user-pool \
    --pool-name "AgentCoreUserPool" \
    --policies '{"PasswordPolicy":{"MinimumLength":8}}' \
    --region "$REGION" --query 'UserPool.Id' --output text)
  [ -n "$POOL_ID" ] && [ "$POOL_ID" != "None" ] || { echo "Error: could not create the user pool." >&2; return 1; }

  # App client (public client, username/password auth)
  CLIENT_ID=$(aws cognito-idp create-user-pool-client \
    --user-pool-id "$POOL_ID" \
    --client-name "AgentCoreClient" \
    --no-generate-secret \
    --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
    --region "$REGION" --query 'UserPoolClient.ClientId' --output text)
  [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "None" ] || { echo "Error: could not create the app client." >&2; return 1; }

  # User with a permanent password
  aws cognito-idp admin-create-user \
    --user-pool-id "$POOL_ID" --username "$COGNITO_USERNAME" \
    --region "$REGION" --message-action SUPPRESS > /dev/null || return 1
  aws cognito-idp admin-set-user-password \
    --user-pool-id "$POOL_ID" --username "$COGNITO_USERNAME" --password "$COGNITO_PASSWORD" \
    --region "$REGION" --permanent > /dev/null || return 1

  DISCOVERY_URL="https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
  export POOL_ID CLIENT_ID DISCOVERY_URL
  cognito_refresh_token
}
```

A **Cognito** user pool (the user directory), an app client allowed to log in with username and password, and a user with a permanent password. The **discovery URL** is where AgentCore finds Cognito's public keys to verify tokens. `AUTH_CONFIG` tells each runtime: accept only JWTs from this pool, issued to this app client. Note it's `source`d, not run, so the exported variables stay in your shell.

```bash title="setup_cognito.sh · getting a token"
# Get a fresh access token (they expire after 1 hour). Call this again any time.
cognito_refresh_token() {
  BEARER_TOKEN=$(aws cognito-idp initiate-auth \
    --client-id "$CLIENT_ID" \
    --auth-flow USER_PASSWORD_AUTH \
    --auth-parameters "USERNAME=$COGNITO_USERNAME,PASSWORD=$COGNITO_PASSWORD" \
    --region "$REGION" --query 'AuthenticationResult.AccessToken' --output text)
  export BEARER_TOKEN

  echo ""
  echo "Pool ID:       $POOL_ID"
  echo "Client ID:     $CLIENT_ID"
  echo "Discovery URL: $DISCOVERY_URL"
  echo "Bearer Token:  ${BEARER_TOKEN:0:25}...  (exported as \$BEARER_TOKEN)"
  echo ""
  echo "Token expires in 1 hour. Refresh with:  cognito_refresh_token"
}
```

> **Tokens expire after one hour:**
> Run `cognito_refresh_token` in the same shell to get a new one. Requests with an expired token are rejected before they reach your agent.

##### Step 2: deploy the MCP server

```bash title="terminal"
agentcore configure -e stock_mcp_server.py --protocol MCP \
  --requirements-file requirements.txt --authorizer-config "$AUTH_CONFIG" \
  --region $REGION --non-interactive
agentcore deploy --agent stock_mcp_server

export MCP_ARN="<stock_mcp_server runtime ARN>"
export STOCK_MCP_URL="https://bedrock-agentcore.$REGION.amazonaws.com/runtimes/$(echo -n $MCP_ARN | jq -sRr '@uri')/invocations?qualifier=DEFAULT"
```

`--protocol MCP` tells Runtime this is an MCP server (port 8000, `/mcp`). Every runtime is reached at a URL built from its ARN; the ARN contains characters like `:` and `/`, so `jq '@uri'` URL-encodes it.

##### Step 3: deploy the Stock Agent

```bash title="terminal"
agentcore configure -e stock_a2a_agent.py --protocol A2A \
  --requirements-file requirements.txt --authorizer-config "$AUTH_CONFIG" \
  --region $REGION --non-interactive
agentcore deploy --agent stock_a2a_agent \
  --env PORT=9000 --env STOCK_MCP_URL=$STOCK_MCP_URL --env AGENT_BEARER_TOKEN=$BEARER_TOKEN

export STOCK_A2A_ARN="<stock_a2a_agent runtime ARN>"
export STOCK_A2A_URL="https://bedrock-agentcore.$REGION.amazonaws.com/runtimes/$(echo -n $STOCK_A2A_ARN | jq -sRr '@uri')/invocations/"

# deploy once more so the agent card advertises its public URL
agentcore deploy --agent stock_a2a_agent --auto-update-on-conflict \
  --env PORT=9000 --env STOCK_MCP_URL=$STOCK_MCP_URL --env AGENT_BEARER_TOKEN=$BEARER_TOKEN \
  --env AGENTCORE_RUNTIME_URL=$STOCK_A2A_URL
```

Why deploy twice? You only learn the agent's public URL after the first deploy, but the agent card must contain that URL (A2A clients send their messages to the URL in the card). The second deploy passes it in as `AGENTCORE_RUNTIME_URL`.

##### Step 4: deploy the Orchestrator

```bash title="terminal"
agentcore configure -e orchestrator.py --protocol A2A \
  --requirements-file requirements.txt --authorizer-config "$AUTH_CONFIG" \
  --region $REGION --non-interactive
agentcore deploy --agent orchestrator \
  --env STOCK_A2A_URL=$STOCK_A2A_URL --env AGENT_BEARER_TOKEN=$BEARER_TOKEN

export ORCH_ARN="<orchestrator runtime ARN>"
```

##### Step 5: test

```bash title="terminal"
curl -s -X POST "https://bedrock-agentcore.$REGION.amazonaws.com/runtimes/$(echo -n $ORCH_ARN | jq -sRr '@uri')/invocations/?qualifier=DEFAULT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: $(uuidgen)$(uuidgen)" \
  -d '{
    "jsonrpc": "2.0", "id": "1", "method": "message/send",
    "params": {"message": {"role": "user",
      "parts": [{"kind": "text", "text": "How is NVDA stock doing today?"}],
      "messageId": "test-1"}}
  }' | jq .
```

The `Authorization` header carries your Cognito token. The session-ID header picks the session (and microVM); two UUIDs glued together comfortably meet the minimum length of 33 characters. The body is the same A2A message as the local test.

##### Step 6: clean up

```bash title="terminal"
agentcore destroy --agent orchestrator --force --delete-ecr-repo
agentcore destroy --agent stock_a2a_agent --force --delete-ecr-repo
agentcore destroy --agent stock_mcp_server --force --delete-ecr-repo
aws cognito-idp delete-user-pool --user-pool-id $POOL_ID --region $REGION
```

The runtimes' CloudWatch log groups (`/aws/bedrock-agentcore/runtimes/…`) are kept so you can read them later; delete them in the CloudWatch console when you no longer need them.

> **Agent-to-agent auth: classroom shortcut vs production:**
> For the demo, the deployed agents reuse *your* Cognito access token (`AGENT_BEARER_TOKEN`) to call each other, and it expires after an hour. Refreshing your token doesn't update the copy inside the deployed agents, so after an hour redeploy steps 3 and 4 with a fresh `$BEARER_TOKEN`. In production, give each agent its own machine identity with AgentCore Identity: the OAuth client-credentials (machine-to-machine) flow from 6.9.

> **Changing the model:**
> Set `BEDROCK_MODEL_ID`, for example with `--env BEDROCK_MODEL_ID=…` on deploy.

## 6.11 Enterprise integration patterns

Once deployed, your agent has to talk to other systems: databases, internal APIs, third-party services, event streams. If you use AgentCore Gateway, it handles much of this (point it at a spec, get tools with auth and error handling built in). The patterns below apply on Lambda or ECS, or whenever you need behaviour Gateway doesn't cover.

#### Databases

Databases are often the first integration to break at scale. An agent serving forty concurrent users, each triggering two or three queries, will exhaust a typical Amazon Aurora (AWS's managed relational database) connection pool within minutes. **Amazon RDS Proxy** sits between your agent and the database and fixes this by multiplexing hundreds of agent requests over a smaller set of real database connections. The agent code doesn't change; the infrastructure absorbs the concurrency.

{{diagram:3}}

*Pool the connections, separate the workloads, lock the keys away.*

Three more rules: keep analytical queries (reports, aggregations) off your transactional database and replicate to **Redshift or Athena** instead; keep conversation state in DynamoDB (as in Section 3); and keep credentials in Secrets Manager with automatic rotation, not in environment variables. Scope the IAM policy to the exact secret ARN the agent needs, and keep database traffic inside a private subnet.

Try it

##### Forty users and a connection pool

**Too many connections.** 120 connections against a limit of 100: 20 queries fail with "too many connections", and the agent's tools start erroring for real users.

Concurrent users = 40 40

Queries each user triggers = 3 3

on Put RDS Proxy in front of the database

Connections asked for

–

Real DB connections

–

Database limit (example)

100

#### External APIs

External APIs fail in ways your agent must handle gracefully. Internal services go down during deployments. Third-party providers enforce **rate limits** and return `429`s. Some endpoints just stop responding, with no error at all.

The rules: set a **timeout** on every call; retry with **exponential backoff**; and return a **structured error the agent can reason about**. *"I couldn't complete the underwriting check; proceeding with a preliminary assessment"* is far better than a raw 500. **Circuit breakers** stop your agent burning time on timeouts when a service is clearly down. For rate-limited APIs, respect `Retry-After` headers, and cache responses when the data doesn't change between calls.

```python title="pattern sketch: a resilient toolillustrative"
import random, time
import httpx
from strands import tool

FAILS, OPEN_UNTIL = 0, 0.0          # a tiny circuit breaker

@tool
def underwriting_check(applicant_id: str) -> dict:
    """Run the underwriting check for a loan applicant."""
    global FAILS, OPEN_UNTIL
    if time.time() < OPEN_UNTIL:                    # breaker open: fail fast
        return {"status": "unavailable", "detail": "Underwriting service is down; "
                "proceed with a preliminary assessment and say so."}
    for attempt in range(3):
        try:
            r = httpx.get(f"https://underwriting.internal/check/{applicant_id}", timeout=5)
            if r.status_code == 429:                   # rate limited: wait as told
                try:
                    wait = float(r.headers.get("Retry-After", 2))
                except ValueError:                     # Retry-After can also be a date
                    wait = 2
                time.sleep(wait)
                continue
            r.raise_for_status()
            FAILS = 0
            return {"status": "ok", "result": r.json()}
        except (httpx.TimeoutException, httpx.HTTPError):
            if attempt < 2:
                time.sleep(2 ** attempt + random.random())  # 1 s, then 2 s (+ jitter)
    FAILS += 1
    if FAILS >= 2:
        OPEN_UNTIL = time.time() + 30                  # stop trying for 30 s
    return {"status": "unavailable", "detail": "Underwriting check failed after 3 tries; "
            "proceed with a preliminary assessment and say so."}
```

> **Think of it like this:**
> A circuit breaker in your house cuts the power when something's wrong, so you don't keep flipping a switch that only makes sparks. A software circuit breaker does the same: after repeated failures it stops calling the broken service for a while and answers "unavailable" instantly, then tries again later.

Try it

##### When the underwriting API misbehaves

**Healthy API.** Healthy API: one quick call, nothing else needed.

**Hanging, no timeout.** no reply… still waiting… (no timeout set). Then: nothing: the request hangs until the platform kills it (for example a `504` after 29 s behind API Gateway).

> **The worst failure is silence.** With no timeout, the tool waits as long as the platform allows while the user stares at a spinner.

**Hanging, with timeouts and retries.** timed out after 5 s → wait 1 s; timed out after 5 s → wait 2 s; timed out after 5 s → give up.

> **Bounded and explained.** Timeouts cap each attempt and backoff spaces the retries, so the agent gets a structured error after 18 seconds instead of hanging. Turn on the circuit breaker to stop paying those 18 seconds on every call. Call again: the breaker is counting failures.

**Circuit breaker open.** open: answered instantly without calling the API · 0 s. Breaker opens after repeated failures: the next calls fail fast instead of waiting. Cool-down over: the breaker is half-open and will let the next call through as a test.

> **Fail fast.** While the breaker is open, nobody waits on a service that's clearly down. The agent gets a clear, structured message and carries on with a preliminary assessment.

**Connection refused.** 500 Internal Server Error: ConnectError

> **A raw error.** The agent can't tell a temporary blip from an outage, and may make something up or give up badly.

**Connection refused, with retries.** refused → wait 1 s; refused → wait 2 s; refused → give up.

> Retries ride out short blips (deployments often cause them). If the service stays down, the agent still gets a message it can reason about.

**Rate limited.** 429 Too Many Requests · Retry-After: 2

> Rate limited, and the tool just passes the error on.

**Rate limited, with retries.** 429 Too Many Requests · Retry-After: 2 → wait 2 s as told; 200 OK · 0.4 s.

> **Respect Retry-After.** The API said when to come back; waiting exactly that long turns a failure into a success. Caching unchanged responses avoids many of these calls entirely.

The API is…

Your tool uses…

on Timeouts + retries with backoff

on Circuit breaker

breaker: closed

Calls

0

Time the user waited

0 s

Pick how the API behaves and what your tool does, then call it a few times.

#### Event-driven integration

Event-driven integration decouples your agent from the systems that feed it. A document lands in Amazon S3; an **Amazon EventBridge** rule picks up the "object created" event and routes it to the agent (you turn on EventBridge notifications for the bucket first). The upstream system doesn't know the agent exists, and the agent doesn't know about the notification system that alerts users when processing finishes.

{{diagram:4}}

*Nobody calls the agent directly. Events flow in, failures are parked for humans, and scheduled jobs run only as long as they need.*

When volume spikes, put an **SQS** queue between EventBridge and the agent to absorb bursts. Messages that fail three times go to a **dead-letter queue**; a CloudWatch alarm fires, someone investigates, and once the issue is fixed they replay the messages. For scheduled work like weekly reports or batch processing, EventBridge Scheduler starts an ECS **RunTask** instead of a Service: it spins up, runs the job and terminates.

#### Synchronous or asynchronous responses?

{{diagram:5}}

*Most production agents do both. These are the same synchronous, polling, streaming and push styles you met in A2A in Section 5.*
