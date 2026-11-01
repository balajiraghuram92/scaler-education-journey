# Glossary

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 6. Course code is provided under the MIT License.

AWS service names, limits, prices and library versions change often. When something here differs from what you see, the current AWS documentation wins.

- **IAM (Identity and Access Management)** — AWS's permission system. Roles and policies say exactly which AWS actions a person or a piece of software may perform on which resources.
- **Container** — A sealed package of your code plus everything it needs to run (Python, libraries, settings), built from a Dockerfile. It runs the same on a laptop and in the cloud.
- **Circuit breaker** — A safety switch around calls to another service: after repeated failures it stops calling for a while and fails fast, then tries again later, so one broken service doesn't stall everything.
- **Graceful degradation** — Keeping a reduced but useful service when something fails, for example answering with a preliminary assessment instead of crashing.
- **Least privilege** — Giving each person or program only the permissions it truly needs, and nothing more, so a mistake or breach can do less damage.
- **Distributed tracing** — Recording one request's journey across many services as a single linked timeline, so you can see where time went and where it failed.
- **AWS Lambda** — AWS's serverless functions: you upload code with a handler, and AWS runs it when an event arrives, scaling from zero to many copies automatically.
- **Amazon API Gateway** — A managed front door for HTTP APIs. It receives web requests and forwards them to a backend such as a Lambda function.
- **Serverless** — Running code without managing servers: the cloud provider starts, scales and stops the compute for you, and you pay only while it runs.
- **Execution environment** — The small, isolated runtime Lambda creates to run your function. It's reused for many invocations while traffic flows, then recycled when idle.
- **Cold start** — The extra delay when a new execution environment has to start and run your setup code before it can handle a request.
- **Provisioned concurrency** — A Lambda setting that keeps a fixed number of environments warm and ready, removing cold starts but costing money even when idle.
- **Lambda durable functions** — A Lambda feature for long workflows: progress is checkpointed, and when the function reruns it skips completed steps and resumes where it left off.
- **AWS SAM** — The Serverless Application Model: a short YAML template format plus a CLI (sam build, sam deploy) for defining and deploying serverless apps.
- **AWS CloudFormation** — AWS's infrastructure-as-code service. A template describes resources; CloudFormation creates them together as a stack and can delete them together.
- **Inference profile** — A Bedrock model ID such as global.anthropic.claude-sonnet-4-6 that can route requests across regions for capacity. IAM must allow the profile and the models behind it.
- **ARN (Amazon Resource Name)** — AWS's unique address for a resource, such as arn:aws:bedrock:us-east-1::foundation-model/…. IAM policies use ARNs to say what may be accessed.
- **Amazon DynamoDB** — AWS's fully managed key-value and document database. Fast lookups by key, no servers to manage; a natural home for session state.
- **Amazon ECS** — Elastic Container Service: AWS's service for running and keeping containers alive, behind load balancers, at the scale you choose.
- **ECS service** — The part of ECS that keeps a chosen number of copies (tasks) of your container running, replaces failed ones and rolls out new versions.
- **FastAPI** — A popular Python framework for building web APIs. You decorate functions with routes like @app.post("/schedule") and it handles the HTTP.
- **Application Load Balancer** — A managed load balancer that receives web traffic and spreads it across healthy targets, such as your containers.
- **Health check** — A regular probe (here, a request to /health or /ping) that tells the platform whether a container is working. Failing ones are taken out of service and replaced.
- **Task definition** — ECS's recipe for a container: which image, how much CPU and memory, which ports, environment variables, roles and where logs go.
- **AWS Fargate** — A way to run containers on ECS without managing servers: you choose CPU and memory per task, AWS provides and patches the machines.
- **VPC (Virtual Private Cloud)** — Your own private network inside AWS, with its own address range, subnets, routing and firewalls.
- **Subnet** — A slice of a VPC's address range in one availability zone. Public subnets route to the internet; private subnets don't.
- **Amazon Bedrock AgentCore** — A set of AWS managed services built specifically for running agents in production: Runtime, Gateway, Identity, Policy, Memory, Observability, Evaluations, Browser and Code Interpreter.
- **Cedar** — An open-source policy language created by AWS for writing precise allow/deny rules. AgentCore Policy uses it to check every tool call before it runs.
- **OpenTelemetry** — An open standard for collecting traces, metrics and logs from software, supported by most monitoring tools.
- **LLM-as-judge** — Using a language model to score another model's or agent's output against criteria such as accuracy, faithfulness or helpfulness.
- **microVM** — A very lightweight virtual machine that starts in a fraction of a second but keeps the strong isolation of a full VM: its own kernel, memory and files.
- **AgentCore starter toolkit** — A Python package (bedrock-agentcore-starter-toolkit) with a Runtime class and an agentcore CLI that configure, deploy, invoke and destroy AgentCore agents.
- **AWS CodeBuild** — AWS's managed build service. AgentCore's toolkit uses it to build your container image in the cloud, so you don't need Docker locally.
- **Amazon ECR** — Elastic Container Registry: AWS's private store for container images, from which Lambda, ECS and AgentCore pull them.
- **ARM64 (Graviton)** — A processor architecture used by AWS Graviton chips and Apple Silicon. Container images must be built for the architecture they'll run on.
- **OpenAPI** — A standard JSON or YAML document describing a REST API: its endpoints, parameters and responses. Also known by its older name, Swagger.
- **AgentCore Gateway** — An AgentCore service that turns OpenAPI specs, Lambda functions, Smithy models and MCP servers into one catalogue of MCP tools, with authentication handled for you.
- **Gateway target** — One API registered with an AgentCore Gateway. The gateway generates one MCP tool for each of its operations.
- **Semantic search** — Finding things by meaning rather than exact words, by comparing embeddings. Gateway uses it to pick the few relevant tools out of hundreds.
- **Embedding** — A list of numbers representing the meaning of a piece of text. Texts with similar meanings have embeddings that are close together.
- **JWT (JSON Web Token)** — A compact, signed token that carries who someone is and what they may do. Services verify the signature instead of asking for a password.
- **Amazon Cognito** — AWS's user directory and sign-in service. It issues OAuth/OIDC tokens (JWTs) that other services can verify.
- **OIDC (OpenID Connect)** — A standard identity layer on top of OAuth 2.0 that lets a service verify who a user is from a token issued by an identity provider.
- **Token vault** — AgentCore Identity's encrypted store for OAuth tokens and API keys, bound to a specific agent and user, with every access logged.
- **Amazon RDS Proxy** — A managed proxy in front of a relational database that pools and shares connections, so many short-lived clients don't exhaust the database.
- **Rate limit** — A cap on how many requests a client may make in a period. Over the limit, APIs answer 429 Too Many Requests, often with a Retry-After header.
- **Exponential backoff** — Retrying after waits that double each time (1 s, 2 s, 4 s…), usually with a little randomness, so retries don't overwhelm a struggling service.
- **Amazon EventBridge** — AWS's event bus: rules match events (like a file landing in S3) and route them to targets; EventBridge Scheduler also runs things on a timetable.
- **Amazon SQS** — Simple Queue Service: a managed message queue. Producers drop messages in, consumers take them out at their own pace, smoothing out bursts.
- **Dead-letter queue** — A side queue where messages go after failing several times, so they can be inspected and replayed instead of being lost or retried forever.
- **Amazon SageMaker** — AWS's platform for building, training and hosting machine-learning models. A SageMaker endpoint serves a trained model's predictions.
- **CIDR notation** — A compact way to write a range of IP addresses: 203.0.113.7/32 means exactly one address; 0.0.0.0/0 means every address on the internet.
- **Listener** — The part of a load balancer that waits on a port (here, 80) and decides where incoming requests go.
- **Target group** — The set of destinations (here, your containers) a load balancer forwards requests to, with a health check that removes unhealthy ones.
- **uvicorn** — A fast Python web server that runs FastAPI apps and listens for HTTP requests on a port.
- **Smithy** — AWS's open-source language for describing service APIs, used to define many AWS services; Gateway can turn Smithy models into tools.
- **AWS Step Functions** — A service for wiring AWS steps into visual workflows (do this, then that, retry on failure), often used to orchestrate other services.
- **AWS KMS** — Key Management Service: AWS's managed service for creating and controlling the encryption keys that protect your data.
- **Amazon Redshift and Athena** — Two AWS analytics services: Redshift is a data warehouse; Athena runs SQL directly over files in S3. Both keep heavy reports off your live database.
- **Internet gateway** — The component that connects a VPC to the public internet. Subnets whose routes point to it are public.
- **EHR (Electronic Health Record)** — The hospital system holding patients' medical histories, diagnoses, procedures and treatments.
