# AgentCore Gateway

## 6.8 AgentCore Gateway

In Section 5 you built MCP servers and clients from scratch, and saw how an agent discovers and calls tools without custom integration code. That works well with a handful of servers whose tool code you write yourself.

Most enterprises don't have MCP servers. They have hundreds of REST APIs described by **OpenAPI** specs, internal services behind authentication layers, and legacy systems nobody wants to touch. Writing an MCP wrapper for each one, with auth, error handling, retries and rate limiting, is a full-time job. And when the API team changes an endpoint or rotates credentials, you're back in the code.

**AgentCore Gateway** bridges that gap. Point it at an OpenAPI spec and it generates MCP tools automatically: no server code to write, no wrapper to maintain. Your agent discovers those tools exactly the way it discovered tools from your Section 5 servers, except now they come from your existing API catalogue.

{{diagram:1}}

*One front door, many backends. The agent sees a single list of MCP tools; the gateway knows which backend each one calls.*

Gateway supports several backend types: an OpenAPI spec for existing REST APIs, a Lambda function for custom logic, or a remote MCP server for tools that already speak the protocol. You can combine them into a single catalogue. The agent doesn't need to know that *check inventory* hits a Lambda function, *send notification* goes through an API Gateway endpoint, and *update CRM* talks to Salesforce. To the agent they're all just tools.

> **Think of it like this:**
> Gateway is a universal travel adapter for your company's APIs. Each API has its own plug shape (REST, Lambda, MCP), but the agent only has one socket: MCP. Gateway converts every plug to that socket, and it also carries the right key for each door it opens.

#### Targets

Gateway calls each registered API a **target**. You register a target by pointing the gateway at an API definition: an OpenAPI spec, a Smithy model, a Lambda function, an API Gateway stage, or a remote MCP server. Gateway reads it, extracts each operation and generates an MCP tool for each, with descriptions, parameter schemas and return types taken straight from the definition.

{{diagram:2}}

*Every operation becomes a tool. Tool names follow `<TargetName>___<operationId>` (three underscores), so tools from different targets never clash.*

Here's how the lab creates a gateway and registers a REST API whose spec is stored in S3. First the gateway itself, the front door:

```python title="agentcore-gateway notebook · create the gateway"
def wait_for(get_fn, ready=("READY",), failed=("FAILED", "CREATE_UNSUCCESSFUL", "UPDATE_UNSUCCESSFUL"), label=""):
    while True:
        status = get_fn()["status"]
        print(f"  {label} status: {status}")
        if status in ready:
            return
        if status in failed:
            raise RuntimeError(f"{label} failed: {get_fn()}")
        time.sleep(5)

gateway = control.create_gateway(
    name=GATEWAY_NAME,
    roleArn=role_arn,
    protocolType="MCP",
    authorizerType="NONE",
    description="Demo gateway that exposes a REST API as MCP tools",
)
GATEWAY_ID = gateway["gatewayId"]
wait_for(lambda: control.get_gateway(gatewayIdentifier=GATEWAY_ID), label="Gateway")

GATEWAY_URL = control.get_gateway(gatewayIdentifier=GATEWAY_ID)["gatewayUrl"]
print("Gateway URL:", GATEWAY_URL)
```

| Argument | Meaning |
| --- | --- |
| `roleArn` | The IAM role the gateway assumes when it works on the agent's behalf (read its config, fetch credentials, read the spec) |
| `protocolType="MCP"` | The gateway speaks MCP to agents |
| `authorizerType` | Who may connect. `CUSTOM_JWT`: OAuth tokens from Cognito, Okta, Entra ID or Auth0, for user-facing apps. `AWS_IAM`: callers sign requests with IAM credentials, for service-to-service calls inside AWS (no separate OAuth provider needed). `NONE`: anyone with the URL, for short-lived demos only. |

> **The lab uses NONE on purpose, and deletes the gateway at the end:**
> It keeps the client code simple in class. The production pattern is `authorizerType="AWS_IAM"` or `"CUSTOM_JWT"`.

Then register the API as a target. You're telling the gateway: "here's an OpenAPI spec in S3: read it and turn every endpoint into an MCP tool."

```python title="agentcore-gateway notebook · register the REST API as a target"
target = control.create_gateway_target(
    gatewayIdentifier=GATEWAY_ID,
    name=TARGET_NAME,
    description="Open-Meteo weather forecast API",
    targetConfiguration={
        "mcp": {
            "openApiSchema": {
                "s3": {"uri": SPEC_URI}
            }
        }
    },
    credentialProviderConfigurations=[{
        "credentialProviderType": "API_KEY",
        "credentialProvider": {
            "apiKeyCredentialProvider": {
                "providerArn": API_KEY_PROVIDER_ARN,
                "credentialParameterName": "X-Api-Key",
                "credentialLocation": "HEADER",
            }
        },
    }],
)
TARGET_ID = target["targetId"]
wait_for(lambda: control.get_gateway_target(gatewayIdentifier=GATEWAY_ID, targetId=TARGET_ID), label="Target")
```

`targetConfiguration` points at the spec. `credentialProviderConfigurations` tells the gateway how to authenticate to *this* API: fetch an API key from the credential provider and send it in the `X-Api-Key` header on every call. The agent never sees that key.

Where this really pays off is composition. Register your customer API, a Lambda function that runs fraud checks and a third-party weather service as targets on the same gateway, and your agent sees one unified tool catalogue on one MCP connection.

#### Semantic search: when there are too many tools

With five or ten tools you can load every definition into the agent's prompt and let the model pick; that's what you did in Section 5. At 200 tools you have a problem: the definitions alone eat a big chunk of the context window, and models get noticeably worse at choosing the right tool as the list grows.

Gateway handles this with **semantic search**. When you register targets, it creates **vector embeddings** of each tool's name, description and parameters and indexes them; the index updates itself as targets change. The search is exposed as one more MCP tool, `x_amz_bedrock_agentcore_search`. You switch it on when you create the gateway, by adding `protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}}` to `create_gateway`. (The lab gateway has one tool and doesn't switch it on, so its tool list shows only `WeatherAPI___getForecast`.)

{{diagram:3}}

*Search first, then call. The agent loads a short list instead of 200 definitions: fewer tokens per request and better tool choices.*

**Can you check Priya's leave balance before I approve her request?** Search query: "employee leave balance". Top matches: `hr_api_get_leave_balance` (0.93), `hr_api_get_employee` (0.74), `hr_api_create_leave_request` (0.70).

**Every request carries all 200 definitions.** That's roughly 30,000 tokens before the user's question is even read, and the model has to pick the right tool from a very long list, which it does less reliably as the list grows. With vague names and no descriptions, it's guessing.

**Poor matches.** The right operation exists, but with a vague name and no description its embedding says almost nothing, so it doesn't make the top three. Search is only as good as your API documentation.

> **Search is only as good as your API documentation:**
> If your OpenAPI spec has well-named operations with clear descriptions, the embeddings are useful and the matches accurate. Operations called `op_17` with no description will be hard for anyone to find, including the search.

Try it

##### 200 tools: load them all, or search?

The user asks

on The API spec is poorly documented (vague names, no descriptions)

Tool definitions in the prompt

–

Rough prompt tokens for tools

–

#### Authentication: inbound and outbound

Any production deployment must answer two questions: **who is allowed to call the gateway**, and **how does the gateway prove its identity to the APIs it calls on your behalf?**

{{diagram:4}}

*Two different keys for two different doors. Auditors in regulated industries check exactly this separation.*

**Inbound** (who can reach the gateway): pick IAM or **JWT**. If your agent already runs on AWS with an IAM role (on Runtime, Lambda or ECS), IAM is the simpler path: grant that role permission to invoke the gateway and you're done. When end-user identity needs to flow through, use JWTs from Cognito, Okta or any OAuth 2.0 provider.

**Outbound** (how the gateway authenticates to each API) is configured per target: an OAuth token for the internal customer API, an API key for a third-party weather service, the gateway's own IAM role for a Lambda function. (OpenAPI targets always expect an OAuth or API-key credential, which is why the lab registers a placeholder key for a free API.) The credentials are kept in secure storage (backed by AWS Secrets Manager), tokens are refreshed and cached so the gateway doesn't hammer downstream identity providers.

The two sets of tokens are completely separate, with different scopes. A downstream API can't take the inbound token and reuse it to impersonate your agent elsewhere. Gateway handles the mechanics of authenticating to downstream APIs, but a bigger question remains: *who is the user behind the request, and what are they allowed to do?* That's the job of AgentCore Identity (6.9).

#### Lab: turn an existing REST API into agent tools

The notebook `agentcore-gateway/gateway_openapi_target.ipynb` turns a real REST API (a subset of the free Open-Meteo forecast API) into an MCP tool with zero tool code, then lets a Strands agent use it.

```text title="the lab in one picture (from the notebook)"
Strands agent ──MCP──► AgentCore Gateway ──HTTPS──► REST API (Open-Meteo weather)
                          │
                          └─ reads the OpenAPI spec from S3 and creates the tools
```

You need AWS credentials with permissions for `bedrock-agentcore:*` (gateway and identity), creating and deleting IAM roles, S3 on the demo bucket, and Secrets Manager (used behind the scenes to store the key).

##### The spec

```json title="agentcore-gateway/weather_openapi.json"
{
  "openapi": "3.0.3",
  "info": {
    "title": "Weather Forecast API",
    "version": "1.0.0",
    "description": "Subset of the free Open-Meteo forecast API (https://open-meteo.com). No API key required."
  },
  "servers": [{ "url": "https://api.open-meteo.com" }],
  "paths": {
    "/v1/forecast": {
      "get": {
        "operationId": "getForecast",
        "summary": "Get current weather and a daily forecast for a latitude/longitude",
        "description": "Returns current temperature and wind, plus daily max/min temperature and precipitation for the next few days.",
        "parameters": [
          { "name": "latitude", "in": "query", "required": true, "description": "Latitude in decimal degrees, e.g. 12.97 for Bangalore", "schema": { "type": "number" } },
          { "name": "longitude", "in": "query", "required": true, "description": "Longitude in decimal degrees, e.g. 77.59 for Bangalore", "schema": { "type": "number" } },
          { "name": "current", "in": "query", "required": false, "description": "Comma-separated current variables", "schema": { "type": "string", "default": "temperature_2m,wind_speed_10m" } },
          { "name": "daily", "in": "query", "required": false, "description": "Comma-separated daily variables", "schema": { "type": "string", "default": "temperature_2m_max,temperature_2m_min,precipitation_sum" } },
          { "name": "timezone", "in": "query", "required": false, "description": "IANA timezone or 'auto'", "schema": { "type": "string", "default": "auto" } },
          { "name": "forecast_days", "in": "query", "required": false, "description": "Number of forecast days (1-16)", "schema": { "type": "integer", "default": 3 } }
        ],
        "responses": {
          "200": {
            "description": "Forecast data",
            "content": { "application/json": { "schema": { "type": "object" } } }
          }
        }
      }
    }
  }
}
```

One operation, `getForecast`, with a clear summary, a description and documented parameters (even an example latitude for Bangalore). That documentation is exactly what the agent reads when deciding how to call the tool.

##### Setup and Step 1: upload the spec to S3

```python title="notebook · names and clients"
import json
import os
import time
import uuid

import boto3

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

session = boto3.Session(region_name=REGION)
account_id = session.client("sts").get_caller_identity()["Account"]
s3 = session.client("s3")
iam = session.client("iam")
control = session.client("bedrock-agentcore-control")

suffix = uuid.uuid4().hex[:6]
GATEWAY_NAME = f"weather-gateway-{suffix}"
TARGET_NAME = "WeatherAPI"
BUCKET = f"gateway-specs-{account_id}-{REGION}"
SPEC_KEY = "weather_openapi.json"
ROLE_NAME = f"AgentCoreGatewayDemoRole-{suffix}"
API_KEY_PROVIDER = f"weather-api-key-{suffix}"

print(f"Account {account_id} | Region {REGION} | Gateway {GATEWAY_NAME}")
```

```python title="notebook · step 1"
try:
    if REGION == "us-east-1":
        s3.create_bucket(Bucket=BUCKET)
    else:
        s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": REGION})
except s3.exceptions.BucketAlreadyOwnedByYou:
    pass

s3.upload_file("weather_openapi.json", BUCKET, SPEC_KEY)
SPEC_URI = f"s3://{BUCKET}/{SPEC_KEY}"
print("Spec uploaded:", SPEC_URI)
```

##### Step 2: store the API credential in AgentCore Identity

```python title="notebook · step 2"
provider = control.create_api_key_credential_provider(
    name=API_KEY_PROVIDER,
    apiKey="demo-key-open-meteo-does-not-need-one",
)
API_KEY_PROVIDER_ARN = provider["credentialProviderArn"]
print("Credential provider:", API_KEY_PROVIDER_ARN)
```

OpenAPI targets need an outbound credential that the gateway attaches to every call. Real APIs use a real key or OAuth; Open-Meteo is free and ignores extra headers, so a placeholder works here. The key is stored in AgentCore Identity, never in your code or the spec.

##### Step 3: an IAM role for the gateway

#### **See the role and its permissions**

```python title="notebook · step 3"
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole",
        "Condition": {
            "StringEquals": {"aws:SourceAccount": account_id},
            "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:*"},
        },
    }],
}

permissions = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": ["bedrock-agentcore:GetGateway"],
         "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:gateway/*"},
        {"Effect": "Allow", "Action": ["bedrock-agentcore:GetResourceApiKey", "bedrock-agentcore:GetWorkloadAccessToken"],
         "Resource": [f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:token-vault/default",
                      f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:token-vault/default/*",
                      f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:workload-identity-directory/*"]},
        {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"],
         "Resource": f"arn:aws:secretsmanager:{REGION}:{account_id}:secret:bedrock-agentcore-identity!*"},
        {"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": f"arn:aws:s3:::{BUCKET}/*"},
    ],
}

role_arn = iam.create_role(RoleName=ROLE_NAME, AssumeRolePolicyDocument=json.dumps(trust_policy))["Role"]["Arn"]
iam.put_role_policy(RoleName=ROLE_NAME, PolicyName="GatewayPermissions", PolicyDocument=json.dumps(permissions))
print("Role:", role_arn)
time.sleep(10)  # let IAM propagate
```

The **trust policy** lets only the AgentCore service, acting for your account, assume the role. The **permissions** are least privilege: read its own gateway config, fetch the API key from the token vault, read the secret, and read objects in the one demo bucket. Nothing else.

##### Steps 4 and 5: create the gateway and the target

These are the two cells you saw above. The target is named `WeatherAPI`, so the gateway creates the tool `WeatherAPI___getForecast`.

##### Step 6: connect a Strands agent

```python title="notebook · step 6"
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient

gateway_client = MCPClient(lambda: streamablehttp_client(GATEWAY_URL))

with gateway_client:
    tools = gateway_client.list_tools_sync()
    print("Tools exposed by the gateway:", [t.tool_name for t in tools])

    agent = Agent(
        model=BedrockModel(model_id=MODEL_ID, region_name=REGION),
        tools=tools,
        system_prompt="You are a travel assistant. Use the weather tools for any weather question.",
    )
    agent("I'm visiting Bangalore and Mumbai this week. What's the forecast for the next 3 days in each city?")
```

The gateway is just an MCP server over **Streamable HTTP**, so this is the same `MCPClient` pattern as Section 5, with `streamablehttp_client(GATEWAY_URL)` instead of a local process.

```text title="outputillustrative; forecasts and wording vary"
Tools exposed by the gateway: ['WeatherAPI___getForecast']

Tool #1: WeatherAPI___getForecast
Tool #2: WeatherAPI___getForecast
Here's your 3-day forecast:

**Bangalore** (12.97, 77.59): 27–28 °C highs, 19–20 °C lows, light showers on day 2.
**Mumbai** (19.08, 72.88): around 32 °C highs, 26 °C lows, mostly dry.

Pack a light umbrella for Bangalore!
```

Notice the model worked out latitude and longitude for each city on its own: the spec told it those are the required parameters.

##### Step 7: clean up

```python title="notebook · step 7"
control.delete_gateway_target(gatewayIdentifier=GATEWAY_ID, targetId=TARGET_ID)
while control.list_gateway_targets(gatewayIdentifier=GATEWAY_ID).get("items"):
    time.sleep(3)
control.delete_gateway(gatewayIdentifier=GATEWAY_ID)
print("Deleted gateway", GATEWAY_ID)

control.delete_api_key_credential_provider(name=API_KEY_PROVIDER)
print("Deleted credential provider", API_KEY_PROVIDER)

iam.delete_role_policy(RoleName=ROLE_NAME, PolicyName="GatewayPermissions")
iam.delete_role(RoleName=ROLE_NAME)
print("Deleted role", ROLE_NAME)

s3.delete_object(Bucket=BUCKET, Key=SPEC_KEY)
s3.delete_bucket(Bucket=BUCKET)
print("Deleted bucket", BUCKET)
```

> **Use your own API:**
> Replace `weather_openapi.json` with your spec and put your real API key (or an OAuth provider) in Step 2. The same gateway can also expose Lambda functions, Smithy models and other MCP servers, and in Section 7 it enforces Cedar policies on every tool call.

## 6.9 AgentCore Identity

Every production agent faces a two-sided authentication problem.

On one side, **callers** must prove who they are before the agent will talk to them, whether the caller is a user, another agent or an automated workflow. On the other side, when the agent calls an **external service** (a CRM, a calendar API, a code repository) it needs credentials for that service. Without the first, anyone can hit your agent endpoint. Without the second, you end up embedding secrets in environment variables or hard-coding API keys, which is how breaches happen.

{{diagram:5}}

*Who's calling, and on whose behalf the agent acts. Identity keeps those two facts connected.*

**Inbound:** Identity supports JWT-based authorisation. Your identity provider (Amazon **Cognito**, Okta, Microsoft Entra ID, or any standard OAuth 2.0 / **OIDC** provider) issues the token, and Identity validates it before the request reaches your agent.

**Outbound:** Identity manages the credentials your agent needs for external services, storing OAuth 2.0 tokens and API keys in a secure **token vault** rather than in your code or configuration. Credentials are encrypted with **AWS KMS**, bound to specific agent-user combinations, and every access is logged for audit.

#### Two kinds of outbound access

{{diagram:6}}

*Many agents need both at once: user-delegated access for personal data and machine-to-machine access for shared resources.*

In your agent code this shows up as decorators. Put `@requires_access_token` or `@requires_api_key` on a function and the SDK fetches, injects and refreshes the credential for you. Identity has built-in credential providers for services like Google, GitHub, Slack, Salesforce and Atlassian, with endpoints and provider-specific settings pre-configured; for anything else you can set up a custom OAuth 2.0 provider.

```python title="pattern sketch with the bedrock-agentcore SDKillustrative"
from bedrock_agentcore.identity.auth import requires_access_token, requires_api_key

# On behalf of the user: OAuth authorisation code flow ("USER_FEDERATION")
@requires_access_token(
    provider_name="google-calendar",          # a credential provider you created
    scopes=["https://www.googleapis.com/auth/calendar.readonly"],
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: print("Ask the user to open:", url),
)
def list_my_events(*, access_token: str):
    ...  # call the Calendar API with access_token

# As itself: OAuth client credentials ("M2M")
@requires_access_token(
    provider_name="warehouse-oauth",
    scopes=["warehouse/read"],
    auth_flow="M2M",
)
def query_warehouse(sql: str, *, access_token: str):
    ...  # call the data warehouse with access_token

# A static API key from the token vault
@requires_api_key(provider_name="weather-api-key")
def get_forecast(city: str, *, api_key: str):
    ...  # call the weather API with api_key
```

Because Identity validates the inbound token *and* manages outbound credentials, it keeps the link between who is calling and what the agent is doing on their behalf. That context, the caller's identity paired with the agent's identity, is what lets the rest of AgentCore enforce per-user, per-action governance.

> **You've already used it:**
> Step 2 of the Gateway lab created an **API key credential provider** in Identity, and the gateway pulled the key from the token vault on every call. The multi-agent lab next uses a **Cognito JWT** for inbound authentication.

> **On Lambda or ECS?:**
> You build credential management yourself: store tokens in Secrets Manager, implement OAuth flows in your app, handle token refresh, manage the security. It works, but it's undifferentiated work that Identity provides as a managed service.
