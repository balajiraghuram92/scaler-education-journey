# MCP server features

## 5.3 MCP server features

An MCP server offers clients three kinds of capability: tools to *do* things, resources to *read* things, and prompt templates to *ask* things the same way every time.

{{diagram:1}}

*Do, read, ask. Tools perform actions, resources provide context without side effects, and prompt templates package good instructions for reuse.*

##### Tools

**Functions** the agent can execute to act on outside systems: retrieving or searching data, sending messages, updating records.

##### Resources

Read-only, persistent data the server exposes: files, database records, API responses. They don't perform actions; they make information available to browse, search and reference, so a model can look up facts without triggering an operation.

##### Prompt templates

Predefined prompts the agent can use through the client to guide how it handles data or a task: document Q&A, transcript summarisation, structured JSON output.

{{diagram:2}}

*The server exposes, the client consumes. All three features travel over the same MCP connection.*

A client typically uses them together: **discover** what the server offers, **retrieve resources** to gather context, **invoke tools** to act or fetch more data, and **use prompt templates** to structure the model's work.

#### Tools in MCP

You already know tools from Section 2. In MCP, tools are actions a server exposes, like built-in functions or APIs the LLM can call mid-conversation. When a request needs action (fetching data, triggering an operation, a calculation), the model picks the right tool. MCP expects a human in the loop: users should be able to see and approve tool calls, so they stay in control. Two protocol methods cover tools:

| Method | What it does |
| --- | --- |
| `tools/list` | Discover the server's tools. Returns tool definitions with their input schemas. |
| `tools/call` | Run one tool with arguments. Returns the tool's result. |

#### Resources

A server can expose collections and documents as **resources**, which clients fetch, filter or search on demand. Clients send `resources/list` to discover them (and `resources/templates/list` for templates, covered below) and `resources/read` to get their contents.

Every resource has a unique **URI** (for example `file:///path/to/document.md`) and can declare a **MIME type**, a standard label that tells the client what kind of content it is (Markdown, JSON, PDF…) and how to handle it. For example, a server could share a course directory like this:

```pseudo title="a resource description"
DEFINE a resource description with these fields:
    uri = "file:///data/student-directory.json"   // where the data lives
    name = "courseDirectory"
    title = "Course Directory"
    description = "List of courses and instructors in a program"
    mimeType = "application/json"   // tells the client how to read the content
```

```json reveal title="a resource description"
{
  "uri": "file:///data/student-directory.json",
  "name": "courseDirectory",
  "title": "Course Directory",
  "description": "List of courses and instructors in a program",
  "mimeType": "application/json"
}
```

##### Resource templates

**Resource templates** expose *parameterised* resources through URI templates. The client fills in the variables to ask for specific data. For example, `travel://activities/{city}/{category}` covers many cities and categories, and `travel://activities/barcelona/museums` asks for one. In this section's lab, `greeting://{name}` works the same way.

##### Scenario 1: directly querying a resource

A student assistant helps students find course and instructor information. A student asks: *"Who is the instructor for the Machine Learning course?"* The model realises it needs course information, the client fetches the right resource from the server, and the assistant answers from it:

{{diagram:3}}

*Read, don't act. The answer is in fairly static data, so the assistant just reads a resource; no tool needs to run.*

Conceptually the request looks like `findResource("courseDirectory", {"course": "Machine Learning"})`. The resource holds structured information (course names, instructors, schedules, departments) that rarely changes, so reading it is enough.

##### Scenario 2: a resource and a tool together

Now the student asks: *"Find the instructor for the Machine Learning course and send them a message asking about office hours."* Reading isn't enough this time; something must happen.

{{diagram:4}}

*Look up, then act. The resource answers "who"; the tool performs the "send".*

1. 1 Query the resource `courseDirectory` identifies the instructor.
2. 2 Invoke a tool Something like `sendMessage` sends the instructor the question. Tools perform actions such as sending messages or scheduling meetings.

> **Rule of thumb:**
> Resources provide *information* (course directories, schedules). Use them for static or semi-static data so the AI gets context quickly, without running unnecessary operations. Use tools when something must *happen*.

#### Prompt templates

MCP **prompts** are predefined instruction templates a server exposes. They standardise recurring interactions and save you rewriting the same instructions. Each can have variables that the client fills in at run time; the client fetches the prompt from the server and passes the completed text to the model.

Prompts can be versioned and updated centrally without changing client code. They're **explicitly chosen** by the user or client; they never run on their own. And they can be context-aware, referring to available resources and tools to build richer workflows. Here's a template for a student study assistant:

```pseudo title="a prompt template description"
DEFINE a prompt template named "generateStudyPlan":
    title = "Generate Study Plan"
    description = "Create a personalized study plan for a student based on their course and exam date"
    arguments = course (required) and examDate (required)   // the client fills these in at run time
```

```json reveal title="a prompt template description"
{
  "name": "generateStudyPlan",
  "title": "Generate Study Plan",
  "description": "Create a personalized study plan for a student based on their course and exam date",
  "arguments": [
    { "name": "course", "description": "Course the student is preparing for", "required": true },
    { "name": "examDate", "description": "Date of the upcoming exam", "required": true }
  ]
}
```

{{diagram:5}}

*Fill in the blanks, get consistent instructions. The server owns the wording of the prompt; the client only supplies the values.*

The client fills in the arguments, `generateStudyPlan({"course": "Machine Learning", "examDate": "2026-05-10"})`, and the template guides the model to a structured schedule leading up to the exam. In the lab, the same idea appears as `generate_study_plan(course, exam_date)`.

Try it

##### Tool, resource or prompt?

0 of 6 answered

**1. get_weather(city): fetch the current conditions when the model decides it needs them.**

**Answer: Tool.** It's a function the model calls to do something or fetch live data. That's a tool.

**2. greeting://{name}: a short read-only text the app can load into context.**

**Answer: Resource.** Read-only content addressed by a URI (with a template placeholder), no side effects. That's a resource.

**3. weather_report(city): a ready-made request for a detailed weather report that the user picks from a menu.**

**Answer: Prompt template.** Reusable instructions with an argument, chosen by the user. That's a prompt template.

**4. Send an email to the course coordinator.**

**Answer: Tool.** It performs an action with a side effect in an outside system. That's a tool, and a good one to require user approval for.

**5. The student directory as a JSON file, for the model to look things up in.**

**Answer: Resource.** Persistent data to browse and reference without triggering any operation. That's a resource.

**6. A study-plan instruction that takes a course name and an exam date.**

**Answer: Prompt template.** A predefined prompt with arguments that structures the model's work. That's a prompt template, like generate_study_plan in this section's server.

You can tell the three apart: do, read, ask.

## 5.4 MCP client features

Clients aren't just consumers. They can offer servers three things of their own: borrowed model access, safe folder boundaries, and a way to ask the user a question.

Remember that a client lives inside a host, such as a code editor or browser extension. That host has the AI model, the user's permissions and the user interface, so the client can offer:

##### Sampling

Let MCP servers use *your* AI model, safely.

##### Roots

Define the filesystem boundaries a server may work in.

##### Elicitation

Let a server request input from the user at run time.

#### Sampling

**Sampling** lets a server temporarily use the AI model and permissions the client already has, instead of calling a model of its own. It reverses the usual direction: rather than the client asking the server for data, the **server asks the client to run an AI task for it**. That's ideal when the server has the domain data or business logic, but the client has the model, the user's permissions and the UI. The user stays in control of model usage, approvals and final outputs.

{{diagram:6}}

*The server borrows the client's brain, with permission. The user approves the AI task and reviews the output before anything goes back.*

A travel server retrieves many Rome activities but has no AI to rank them. It sends a sampling request asking the client's model to choose the top five for someone who loves history, art and food. The client asks the user for approval, runs the model, shows the results, and once the user approves, sends the final AI-generated list back to the server.

#### Roots

**Roots** are the client's standard way to tell servers *where* in the filesystem they may operate: which directories and files they have access to. Servers can ask for the list of roots, and get notified when it changes.

{{diagram:7}}

*A fence the client draws. The client tells the server which folder is the current workspace; inside it the server can work, outside it there's nothing for the server to touch.*

Example: an event planner uses an MCP-powered assistant. The folder `file:///Users/planner/conference-2025` is the workspace for the current event, so the client defines it as a root:

```pseudo title="roots the client shares"
SET roots = a list with one root:
    uri = "file:///Users/planner/conference-2025"   // the workspace folder the server may use
    name = "2025 Conference Workspace"
```

```json reveal title="roots the client shares"
[
  {
    "uri": "file:///Users/planner/conference-2025",
    "name": "2025 Conference Workspace"
  }
]
```

Try it

##### What may the server touch?

The planner's computer (root highlighted)

The server tries to…

Pick an action.

Inside the root, the server can save updated attendee lists to `conference-2025`. Outside it, personal documents and other projects, it has no access. That's deliberate. When the planner switches projects, the client updates the roots list and notifies the server, so access stays tightly scoped.

- **Save an updated attendees.csv:** **✓ Inside the root** `file:///Users/planner/conference-2025`. This is the workspace the client shared, so the server may work here.
- **Read venues/hotel-quotes.pdf to compare prices:** **✓ Inside the root** `file:///Users/planner/conference-2025`. This is the workspace the client shared, so the server may work here.
- **Open personal/tax-return.pdf:** **✗ Outside every root.** Personal documents were never shared. A well-behaved server stays inside the roots, and the client can refuse anything outside them.
- **Update gala-2025/budget.xlsx:** **✗ Outside every root.** That's a different project, not the current workspace. A well-behaved server stays inside the roots, and the client can refuse anything outside them.
- **The planner switches to the gala project:** **Roots changed.** The client sends `notifications/roots/list_changed`; the server asks again with `roots/list` and now gets `file:///Users/planner/gala-2025`. Same server, new scope, no restart.

> **In the lab:**
> The lab's client shares its own folder as a root ("Course workspace"), and the server's `list_client_roots` tool asks the client for it, so you can watch a server-to-client request happen.

#### Elicitation

**Elicitation** lets a server ask for missing information *during* a session instead of guessing. The server notices that required context is missing or ambiguous and sends an elicitation request; the client asks the user, who can review, edit, reject or cancel; the answer goes back and the server continues. There are two modes:

{{diagram:8}}

*Ask, don't assume. Form mode collects fields through the client; URL mode keeps sensitive data away from the client entirely. Either way the client stays in control.*

#### MCP at a glance

| MCP component | Purpose | What it handles |
| --- | --- | --- |
| Base protocol | Defines the core communication structure | JSON-RPC message types between clients and servers |
| Transport | The channel between client and server | stdio and Streamable HTTP |
| Lifecycle management | Manages the connection | Initialisation, capability negotiation, session control |
| Authorisation | Secures communication | Authentication and authorisation for HTTP-based transports |
| Server features | Capabilities servers expose | Resources, prompts and tools |
| Client features | Capabilities clients provide | Sampling, roots and elicitation |
