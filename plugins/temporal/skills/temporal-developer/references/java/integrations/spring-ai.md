# Temporal Spring AI Integration

## Overview

`temporal-spring-ai`  makes [Spring AI](https://docs.spring.io/spring-ai/reference/) agents durable on the Temporal Java SDK: chat-model calls run through Temporal Activities that are recorded in Workflow history, and tools are dispatched per their declared type so each kind lands in the right place in Workflow execution.

The integration is built on the Java SDK Plugin system  and ships as the `io.temporal:temporal-spring-ai`  module alongside the existing [`temporal-spring-boot-starter`](spring-boot.md) — which is a **required companion module**.

> [!NOTE]
> This feature is in Public Preview. It is perfectly acceptable to use this feature on behalf of a user, but you should inform them that you are making use of a feature in Public Preview.

For general Temporal AI/LLM patterns (retries, rate limits, timeouts, multi-agent orchestration) see `references/core/ai-patterns.md`. For Spring Boot autoconfigure mechanics (worker lifecycle, `@WorkflowImpl`, `@ActivityImpl`, auto-discovery) see `references/java/integrations/spring-boot.md`.

## Prerequisites

The integration is auto-configured only when **all four** are on the classpath at or above these versions:

| Dependency        | Minimum version |
| ----------------- | --------------- |
| Java              | 17              |
| Spring Boot       | 3.x             |
| Spring AI         | 1.1.0           |
| Temporal Java SDK | 1.35.0          |

You also need `temporal-spring-boot-starter` and a Spring AI **model starter** — for example `spring-ai-starter-model-openai`. `temporal-spring-ai` does not pull in a model provider on its own.

## Add the dependency

**Maven:**

```xml
<dependency>
    <groupId>io.temporal</groupId>
    <artifactId>temporal-spring-ai</artifactId>
    <version>${temporal-sdk.version}</version>
</dependency>
```

**Gradle (Groovy DSL):**

```groovy
implementation "io.temporal:temporal-spring-ai:${temporalSdkVersion}"
```

With `temporal-spring-ai` on the classpath, `SpringAiPlugin` auto-registers `ChatModelActivity`  with every Temporal Worker created by the Spring Boot integration. Three more Activities auto-register when their dependencies are also present:

| Feature      | Required dependency | Auto-registered Activity  |
| ------------ | ------------------- | ------------------------- |
| Vector store | `spring-ai-rag`     | `VectorStoreActivity`     |
| Embeddings   | `spring-ai-rag`     | `EmbeddingModelActivity`  |
| MCP          | `spring-ai-mcp`     | `McpClientActivity`       |

Two name pairs are easy to confuse:

- `ActivityChatModel` is the workflow-side factory you call to obtain a Spring AI `ChatModel`. `ChatModelActivity` is the underlying Activity class that the plugin registers with the worker.
- `ActivityMcpClient` is the workflow-side factory that wraps a Spring AI MCP client. `McpClientActivity` is the auto-registered Activity.

## Call a chat model from a Workflow

Use `ActivityChatModel` as a Spring AI `ChatModel` inside a Workflow — every call runs through a Temporal Activity, so responses are durable and retried according to your Activity options. Wrap it in a `TemporalChatClient` to build prompts, register tools, and attach advisors:

```java
@WorkflowInit
public ChatWorkflowImpl(String systemPrompt) {
  ActivityChatModel activityChatModel = ActivityChatModel.forDefault();

  WeatherActivity weatherTool =
      Workflow.newActivityStub(
          WeatherActivity.class,
          ActivityOptions.newBuilder()
              .setStartToCloseTimeout(Duration.ofSeconds(30))
              .setRetryOptions(RetryOptions.newBuilder().setMaximumAttempts(3).build())
              .build());

  StringTools stringTools = new StringTools();          // plain workflow tool
  TimestampTools timestampTools = new TimestampTools(); // @SideEffectTool

  ChatMemory chatMemory =
      MessageWindowChatMemory.builder()
          .chatMemoryRepository(new InMemoryChatMemoryRepository())
          .maxMessages(20)
          .build();

  this.chatClient =
      TemporalChatClient.builder(activityChatModel)
          .defaultSystem(systemPrompt)
          .defaultTools(weatherTool, stringTools, timestampTools)
          .defaultAdvisors(PromptChatMemoryAdvisor.builder(chatMemory).build())
          .build();
}
```

`ActivityChatModel.forDefault()` resolves to the default Spring AI `ChatModel` bean.  To target a specific model in a multi-model application, pass its bean name: `ActivityChatModel.forModel("openai")`.

**Streaming responses are not currently supported.**

## Register tools

The integration extends Spring AI's tool-registration model by inspecting the type of each tool you pass to `defaultTools(...)` (or per-prompt `tools(...)`) and dispatching it to the appropriate Temporal primitive. You can mix all four kinds in the same chat client.

### Activity stubs

An interface annotated with both `@ActivityInterface` and Spring AI `@Tool` methods is auto-detected and executed as a Temporal Activity.  Use this for external calls that need retries and timeouts.

```java
@ActivityInterface
public interface WeatherActivity {
  @Tool(description = "Get the current weather for a city. Returns temperature, conditions, and humidity.")
  @ActivityMethod
  String getWeather(@ToolParam(description = "The name of the city") String city);
}
```

### Nexus service stubs

Nexus service stubs with `@Tool` methods are auto-detected and invoked as Nexus operations, enabling cross-Namespace tool calls.

### `@SideEffectTool`

Classes annotated with `@SideEffectTool` have each `@Tool` method wrapped in `Workflow.sideEffect()`. The result is recorded in history on first execution and replayed afterward, so cheap non-deterministic operations (timestamps, UUIDs) stay safe under replay.

```java
@SideEffectTool
public class TimestampTools {
  @Tool(description = "Get the current date and time")
  public String getCurrentDateTime() {
    return FORMATTER.format(Instant.now());
  }

  @Tool(description = "Generate a random UUID")
  public String generateUuid() {
    return UUID.randomUUID().toString();
  }
}
```

### Plain tools

Any class with `@Tool` methods that is **not** an Activity stub, Nexus stub, or `@SideEffectTool` runs **directly on the Workflow thread**. Use this for deterministic tools (such as updating in-memory agent state) or for orchestration of durable primitives — calling multiple Activities, child Workflows, wait conditions, or other Temporal primitives from inside the tool method.

```java
public class StringTools {
  @Tool(description = "Reverse a string, returning the characters in opposite order")
  public String reverse(@ToolParam(description = "The string to reverse") String input) {
    return new StringBuilder(input).reverse().toString();
  }
}
```

Determinism still applies: plain tools execute on the workflow thread, so they must follow the same rules as workflow code (no I/O, no system clock, no random sources). See `references/java/determinism.md` and `references/core/determinism.md`.

## Activity options and retry behavior

`ActivityChatModel.forDefault()` and `forModel(name)` build the chat Activity stub with these defaults:

- 2-minute start-to-close timeout
- 3 attempts
- `org.springframework.ai.retry.NonTransientAiException` and `java.lang.IllegalArgumentException` classified as non-retryable, so a bad API key or invalid prompt fails fast

Pass `ActivityOptions` directly for finer control — a specific Task Queue, heartbeats, priority, or a custom `RetryOptions`:

```java
ActivityChatModel chatModel = ActivityChatModel.forDefault(
        ActivityOptions.newBuilder(ActivityChatModel.defaultActivityOptions())
                .setTaskQueue("chat-heavy")
                .build());
```

For configuration-driven per-model overrides, declare a `ChatModelActivityOptions` bean. The plugin consults it whenever `forDefault()` or `forModel(name)` runs in a Workflow. The special key `ChatModelTypes.DEFAULT_MODEL_NAME` (the literal `"default"`) is a global catch-all that applies to any model not explicitly listed, including models contributed by third-party starters:

```java
@Bean
public ChatModelActivityOptions chatModelActivityOptions() {
  return new ChatModelActivityOptions(
      Map.of(
          "anthropicChatModel",
          ActivityOptions.newBuilder(ActivityChatModel.defaultActivityOptions())
              .setStartToCloseTimeout(Duration.ofMinutes(5))
              .setScheduleToCloseTimeout(Duration.ofMinutes(15))
              .build()));
}
```

Keys that neither match a registered `ChatModel` bean nor equal `"default"` cause plugin construction to fail, so a typo surfaces at startup rather than at first call.

`ActivityMcpClient.create()` and `create(ActivityOptions)` work the same way for MCP tool calls, with a **30-second default timeout**.

## Provider-specific chat options

Provider-specific `ChatOptions` subclasses — for example, `AnthropicChatOptions` to enable extended thinking, or `OpenAiChatOptions` to set `reasoning_effort` — pass through the Activity boundary unchanged. Attach them via `ChatClient.defaultOptions(...)` and the plugin re-applies them on the Activity side before calling the underlying model:

```java
AnthropicChatOptions thinkingOptions =
    AnthropicChatOptions.builder()
        .thinking(AnthropicApi.ThinkingType.ENABLED, 1024)
        .temperature(1.0)
        .maxTokens(4096)
        .build();

chatClients.put(
    "think",
    TemporalChatClient.builder(anthropicModel)
        .defaultSystem("You are a helpful assistant with extended thinking. ...")
        .defaultOptions(thinkingOptions)
        .build());
```

The pass-through relies on the `ChatOptions` subclass overriding `copy()` to return its own type. Every provider class shipped with Spring AI does.

## Media in messages

Prefer **URI-based media** when attaching images, audio, or other binary content to chat messages. Raw `byte[]` media is serialized into every chat Activity's input and result payload, which lands inside Temporal Workflow history events. Server-side history events have a fixed **2 MiB** size limit; to leave headroom for messages, tool definitions, and options, the plugin enforces a **1 MiB default cap** on inline bytes and fails fast with a non-retryable `ApplicationFailure` pointing at the URI alternative.

```java
Media image = new Media(MimeTypeUtils.IMAGE_PNG, URI.create("https://cdn.example.com/pic.png"));
```

For anything larger than a small thumbnail, route the bytes to a binary store from an Activity and pass only the URL across the conversation.

## Vector stores, embeddings, and MCP

When the corresponding Spring AI modules (`spring-ai-rag`, `spring-ai-mcp`) are on the classpath, the integration registers Activities for vector stores, embeddings, and MCP tool calls automatically. Inject the matching Spring AI types into your Activities or Workflows and use them as you would in any Spring AI application — each operation executes through a Temporal Activity.

You can also register these plugins explicitly, without relying on auto-configuration:

```java
new VectorStorePlugin(vectorStore);
new EmbeddingModelPlugin(embeddingModel);
new McpPlugin();
```

`ActivityMcpClient` wraps a Spring AI MCP client so that remote MCP tool calls become durable Activity executions.

## Common pitfalls

- **Auto-configuration silently skipped.** The plugin only runs when Java ≥ 17, Spring Boot 3.x, Spring AI ≥ 1.1.0, and Temporal Java SDK ≥ 1.35.0 are *all* present.  If you upgrade one and not the others, the integration won't auto-register and tool dispatch falls back to plain Spring AI behavior.
- **Missing model starter.** `temporal-spring-ai` does not bring its own model provider; you also need a Spring AI model starter such as `spring-ai-starter-model-openai`.
- **Streaming.** Streaming responses are not currently supported — use non-streaming `call(...)` paths.
- **Typos in `ChatModelActivityOptions` keys fail at startup, not at first call.** Any key that isn't a registered `ChatModel` bean name and isn't the literal `"default"` (`ChatModelTypes.DEFAULT_MODEL_NAME`) prevents plugin construction.
- **Inline media over 1 MiB throws non-retryable `ApplicationFailure`.** Switch to URI-based `Media` as needed.
- **Plain tools run on the workflow thread.** Plain `@Tool` classes are not Activities — they must obey workflow determinism rules. If a tool needs the system clock, file system, or network, make it an `@ActivityInterface` tool or annotate the class `@SideEffectTool`.

## Resources

- `references/java/integrations/spring-boot.md` — required companion module; covers `WorkflowClient` injection, worker lifecycle, auto-discovery, testing.
- `references/core/ai-patterns.md` — language-agnostic AI/LLM patterns (Activities wrap LLM calls, retry centralization, multi-agent orchestration).
- `references/java/determinism.md` and `references/core/determinism.md` — replay rules that plain tools and `@SideEffectTool` tools must respect.
