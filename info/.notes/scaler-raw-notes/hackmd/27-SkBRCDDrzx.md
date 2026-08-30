Source: https://hackmd.io/@XRwJaQu1Qxad2vlmG3_I1w/SkBRCDDrzx

# Factory Pattern for Service Abstraction: Comprehensive Summary

## Section 1: The Problem — Hardcoding Which Provider to Call

**Key Concept**: The core issue occurs when deciding *which class* to instantiate only becomes known at runtime, based on configuration values, user choices, or vendor availability.

**Problem 1 - Open/Closed Principle Violation**: A straightforward if/else chain for selecting notification channels (SMS, Email, Push) requires reopening and modifying previously-tested code whenever a new channel is needed. This violates the principle that code should be open for extension but closed for modification.

**Problem 2 - Duplicated Decision Logic**: When multiple services need identical selection logic, copy-pasting the same conditional blocks across files means adding a new provider requires coordinated edits in multiple locations.

**Real-World Example - AI Providers**: A `ChatService` hardcoded directly to `OpenAIClient` cannot accommodate Anthropic or Gemini without internal restructuring. This tight coupling creates production risk—an outage at one vendor brings down the entire feature without failover capability.

**Solution Direction**: Move selection logic into a dedicated factory class, allowing `ChatService` to depend solely on an interface (`AIServiceClient`), not specific implementations.

---

## Section 2: Factory Method — The Core Idea

**Definition**: "A method whose only job is to CREATE and RETURN an object of another, usually related, class."

**Implementation - AIServiceClientProvider**:
```java
class AIServiceClientProvider {
  static AIServiceClient getClient(String provider) {
    if (provider.equals("openai")) return new OpenAIClient();
    if (provider.equals("anthropic")) return new AnthropicClient();
    if (provider.equals("gemini")) return new GeminiClient();
    throw new IllegalArgumentException("Unknown provider: " + provider);
  }
}
```

**Impact on ChatService**: Now depends only on the `AIServiceClient` interface; configuration changes simply pass a different provider string to the factory without modifying `ChatService` itself.

**Critical Distinction - Strict GoF vs. Practical**:
- **Strict Gang-of-Four Factory Method**: Uses abstract methods overridden by subclasses; polymorphism determines which concrete class gets created
- **Simple/Static Factory** (what this builds): A single static method using conditional logic and string parameters; more common in real codebases but technically not one of the original 23 GoF patterns

**Single Responsibility Risk**: Factory classes accumulate unrelated factory methods (AI clients, payment gateways, storage) violating SRP. Each object family should have its dedicated factory.

---

## Section 3: Abstract Factory — When One Provider Needs a Family of Objects

**When It Applies**: Real AI SDKs provide multiple related objects—chat clients, embeddings clients, moderation clients—that must originate from the same vendor to ensure compatibility.

**Core Benefit**: Guarantees a matched, compatible family of objects. Prevents mixing OpenAI's chat client with Gemini's moderation client (different auth schemes, response formats, rate limits).

**Interface Structure**:
```java
interface AIProviderFactory {
  ChatClient createChatClient();
  EmbeddingsClient createEmbeddingsClient();
  ModerationClient createModerationClient();
}
```

Each concrete factory (OpenAIProviderFactory, AnthropicProviderFactory) implements all methods, ensuring consistency within a vendor family.

**Overkill Scenario**: For applications needing only a single client type per vendor, a plain Factory Method suffices. Abstract Factory earns its complexity only when genuinely related objects must stay matched.

**Risk**: Letting callers construct some family members through the factory while directly instantiating others with `new` defeats the entire matched-family guarantee.

---

## Section 4: Real Example — Building an AI Service Client

**Step 1 - Naive Approach**: Each provider implements `AIServiceClient`, but `ChatService` contains its own if/else logic for selection, recreating the Section 1 problem.

**Step 2 - Factory-Based Solution**:
```java
public class ChatService {
  private final AIServiceClient client;
  ChatService(String provider) {
    this.client = AIServiceClientProvider.getClient(provider);
  }
  String getResponse(String prompt) {
    return client.complete(prompt);
  }
}
```

**Configuration Change Impact**: Switching from OpenAI to Anthropic only changes the provider string passed to the constructor. `ChatService.getResponse()` executes identically because it communicates through the interface, not concrete implementations.

---

## Section 5: Coding It Properly — Failover as a Second Motivation

**Real Production Driver**: Beyond code organization, factory abstraction enables automatic failover when a primary vendor experiences an outage.

**Failover Implementation**:
```java
public String getResponse(String prompt) {
  for (String provider : providerPriority) {
    try {
      AIServiceClient client = AIServiceClientProvider.getClient(provider);
      return client.complete(prompt);
    } catch (Exception e) { /* try next */ }
  }
  throw new RuntimeException("All providers failed");
}
```

**Why This Works**: The loop only interacts with the `AIServiceClient` interface, never concrete vendor classes. No changes to existing implementations or the factory itself are required—failover becomes a small, isolated addition.

**Logging Necessity**: The `catch` block must log failure details; silent exceptions transform diagnosable outages into mysteries.

---

## Section 6: Practical Factory — Centralizing, Not Eliminating, the Decision

**Honest Reality**: Factories don't eliminate conditional logic; they concentrate it into exactly one well-known location.

**Trade-off**: Moving an if/else chain from multiple files into one dedicated method prevents duplicate logic but doesn't erase the branching entirely. This remains the pattern's core value—single source of truth rather than elimination.

---

## Section 7: AI Corner — The Factory That Looks Extensible but Isn't

**The Test**: "If a new provider needs integration next month by a different team without touching this factory class, how does that happen?"

**Honest Assessment of Naive Factory**: An if/else factory still requires reopening `AIServiceClientProvider.getClient()` to add new branches—this remains an Open/Closed Principle violation despite appearing centralized.

**Registry-Backed Solution**:
```java
public class AIServiceClientFactory {
  private static final Map<String, Supplier<AIServiceClient>> registry
    = new HashMap<>();

  public static void register(String provider,
      Supplier<AIServiceClient> creator) {
    registry.put(provider, creator);
  }

  public static AIServiceClient createClient(String provider) {
    return registry.get(provider).get();
  }
}

// Bootstrap code:
AIServiceClientFactory.register("openai", OpenAIClient::new);
// Later, separate team:
AIServiceClientFactory.register("mistral", MistralClient::new);
```

**Key Mechanism**: `Supplier<AIServiceClient>` represents deferred object construction; `ClassName::new` is a method reference to that class's constructor. New providers register themselves without the factory class reopening.

**Real Extensibility**: This design genuinely supports independent team additions through registration calls, not factory-class edits.

---

## Section 8: Beyond register() — Java's Built-In ServiceLoader

**Purpose**: The JDK-native `ServiceLoader` discovers and instantiates interface implementations automatically at runtime without any shared registration code.

**Mechanism**: Each provider module includes a plain text file at:
```
src/main/resources/META-INF/services/com.example.ai.AIServiceClient
```
Contents:
```
com.example.ai.OpenAIClient
```

**Usage**:
```java
ServiceLoader<AIServiceClient> loader =
  ServiceLoader.load(AIServiceClient.class);
for (AIServiceClient client : loader) { /* use each */ }
```

**Advantage Over Hand-Rolled Registry**: No shared bootstrap file listing all providers; each module self-registers through its own metadata file.

**Real-World Applications**:
- JDBC drivers auto-discover via `DriverManager` without `DriverManager` knowing every database vendor
- SLF4J logging bindings (`LoggerFactory`) detect available backends through classpath scanning

**Limitations**:
- Requires no-argument constructors (configuration must come from environment or files)
- Discovery happens at startup; runtime additions need application restart
- Typos in `META-INF/services` file paths fail silently

---

## Section 9: Production Use Cases

**Common Real-World Instances**:
- LLM provider abstraction (OpenAI/Anthropic/Gemini swapping)
- Payment gateways (Razorpay, Stripe, PayPal unified interface)
- Cloud storage SDKs (S3, GCS, Azure Blob behind common abstraction)
- JDBC driver selection based on connection URL prefix
- SLF4J logging backend discovery

**2026 Backend Context**: Nearly every backend team integrating LLM APIs faces this exact problem; the pattern applies universally beyond AI domains.

---

## Section 10: Common Pitfalls Summary

**Critical Issues**:
1. Editing dispatch methods for new types—OCP violation
2. Duplicating if/else across services—multiple coordinated edits required
3. Conflating strict GoF Factory Method with Simple Factory—different dispatch mechanisms
4. Single factory class handling unrelated object families—SRP violation
5. Abstract Factory when objects don't need family matching—unnecessary overhead
6. Mixed factory and direct `new` construction—breaks Abstract Factory guarantees
7. Direct instantiation outside factory—scattered edit points
8. Accepting "compiles today" as extensibility proof—misses real test
9. Registry-order bugs and silent failures—edge cases in production
10. Expecting `ServiceLoader` to detect new JARs at runtime—restart required

---

## Section 11: Key Terminology

| Term | Definition |
|------|-----------|
| **Factory Method (loose)** | Any method creating/returning another object based on input |
| **Factory Method (strict GoF)** | Abstract method overridden by subclasses; polymorphism dispatches |
| **Simple/Static/Practical Factory** | Single method using parameter and conditionals to pick class |
| **Abstract Factory** | Interface grouping related factory methods, guaranteeing matched families |
| **Registry-backed factory** | Lookup-table-driven (`Map<String, Supplier<T>>`) instead of hardcoded conditionals |
| **`Supplier<T>`** | Functional interface representing deferred object construction |
| **Method reference** | `ClassName::new` syntax for constructor references |
| **`ServiceLoader`** | JDK mechanism auto-discovering interface implementations via `META-INF/services` |
| **Failover** | Automatic switching to backup when primary fails |

---

## Section 12: Frequently Asked Interview Questions

**Distinction from Prior Patterns**: Factory solves the earlier decision stage (which class to build) versus Prototype/Registry (how to safely copy or retrieve already-known objects).

**Factory Method vs. Abstract Factory**: Former creates single objects; latter groups related factory methods guaranteeing matched families across multiple object types.

**OCP and Duplication Problems**: Hardcoding vendor classes forces reopening tested code for each new vendor (OCP violation) and requires duplicating selection logic across multiple services.

**Honest Factory Limitation**: Factories don't eliminate branching logic; they centralize it into exactly one known location for single source of truth.

**Extensibility Test**: Genuine extensibility means different teams can add providers without touching shipped factory code—an if/else factory fails this test.

**`ServiceLoader` Advantage**: No shared registration code; each module self-registers through metadata files, enabling true independent extension.

**Failover Motivation**: Abstraction enables automatic provider switching during outages without modifying existing implementations or factory internals.

---

## Section 13: Self-Check Questions

These 12 questions prompt readers to:
- Explain OCP/duplication problems
- Rewrite GoF Factory Method patterns
- Trace execution flows
- Compare design alternatives
- Evaluate Abstract Factory guarantees
- Distinguish registry implementations
- Analyze failover sequences
- Write `META-INF/services` files
- Determine Abstract Factory necessity
- Question extensibility claims
- Compare pattern purposes

---

## Section 14: Further Reading

Recommended sources include the original Gang-of-Four design patterns book, Joshua Bloch's *Effective Java* (Item 1), official Java documentation for `ServiceLoader`, JDBC `DriverManager` source, and SLF4J binding documentation for real production examples.

---

## Section 15: Homework

**Practical Exercises**:
1. Implement registry-backed factory; add fourth provider without factory edits
2. Extend failover logging to track which provider served each request
3. Prompt AI to design payment gateway factory; test extensibility claims
4. Push completed code to GitHub on `factory-service-abstraction-lecture-complete` branch

Note: This is a detailed structured summary (not verbatim) — the initial verbatim-extraction attempt was refused by the fetch tool on copyright grounds; this summary-style retry succeeded instead.
