# Temporal Spring Boot Integration

## Overview

`temporal-spring-boot-starter` auto-configures workers, registers workflow/activity implementations, and exposes `WorkflowClient` as a Spring bean. This eliminates the manual `WorkflowServiceStubs` → `WorkflowClient` → `WorkerFactory` setup required without Spring.

## Dependency Setup

Maven:
```xml
<dependency>
    <groupId>io.temporal</groupId>
    <artifactId>temporal-spring-boot-starter</artifactId>
    <version>[1.0,)</version>
</dependency>
```

Gradle:
```groovy
implementation 'io.temporal:temporal-spring-boot-starter:1.+'
```

The starter transitively includes `temporal-sdk` and the autoconfigure module. You can declare both `temporal-sdk` and `temporal-spring-boot-starter` explicitly, but the starter alone is sufficient.

## Minimal Configuration

`application.properties`:
```properties
spring.temporal.connection.target=local
spring.temporal.start-workers=true
spring.temporal.workersAutoDiscovery.packages=greetingapp
```

`application.yml` equivalent:
```yaml
spring:
  temporal:
    connection:
      target: local  # shorthand for localhost:7233
    start-workers: true
    workersAutoDiscovery:
      packages:
        - greetingapp
    workers:
      - task-queue: greeting-queue
        name: greeting-worker
```

For self-hosted Temporal, replace `local` with the server address:
```properties
spring.temporal.connection.target=temporal.internal:7233
```

## Interface Design + Spring Annotation Layering

The key concept: Temporal SDK annotations go on **interfaces**, Spring Boot autoconfigure annotations go on **implementation classes**. This is identical to non-Spring usage at the interface level.

### Workflow Interface (unchanged from non-Spring)
```java
package greetingapp;

import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface GreetingWorkflow {
    @WorkflowMethod
    String greet(String name);
}
```

### Workflow Implementation
```java
package greetingapp;

import io.temporal.activity.ActivityOptions;
import io.temporal.spring.boot.WorkflowImpl;
import io.temporal.workflow.Workflow;

import java.time.Duration;

// @WorkflowImpl replaces manual worker.registerWorkflowImplementationTypes()
// No @Component — workflows are NOT Spring beans; Temporal creates a new instance per execution
@WorkflowImpl(taskQueues = "greeting-queue")
public class GreetingWorkflowImpl implements GreetingWorkflow {

    // Activity stubs created via Workflow.newActivityStub() as usual
    private final GreetActivities activities = Workflow.newActivityStub(
        GreetActivities.class,
        ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofSeconds(30))
            .setTaskQueue("greeting-queue")
            .build()
    );

    @Override
    public String greet(String name) {
        return activities.greet(name);
    }
}
```

### Activity Interface (unchanged from non-Spring)
```java
package greetingapp;

import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface GreetActivities {
    @ActivityMethod
    String greet(String name);
}
```

### Activity Implementation
```java
package greetingapp;

import io.temporal.spring.boot.ActivityImpl;
import org.springframework.stereotype.Component;

// @Component makes this a Spring bean — dependencies can be injected normally
// @ActivityImpl replaces manual worker.registerActivitiesImplementations()
@Component
@ActivityImpl(taskQueues = "greeting-queue")
public class GreetActivitiesImpl implements GreetActivities {

    private final GreetingService greetingService;

    // Constructor injection works because this is a Spring bean
    public GreetActivitiesImpl(GreetingService greetingService) {
        this.greetingService = greetingService;
    }

    @Override
    public String greet(String name) {
        return greetingService.composeGreeting(name);
    }
}
```

## Auto-Discovery

Auto-discovery is how the autoconfigure finds and registers implementations without explicit configuration. It requires **both** of the following:

1. `@WorkflowImpl(taskQueues = "...")` or `@ActivityImpl(taskQueues = "...")` on the implementation class
2. `spring.temporal.workersAutoDiscovery.packages` pointing to a package that contains those classes

Missing either one results in silent non-registration — no error, nothing polls the task queue.

The `taskQueues` attribute routes implementations to the right worker when multiple task queues exist. A worker configured with task queue `"greeting-queue"` only picks up implementations annotated with `taskQueues = "greeting-queue"`.

**Important:** `@ActivityImpl(taskQueues = "greeting-queue")` only registers the activity bean with that worker. It does not route individual activity task executions. Inside the workflow, `ActivityOptions.setTaskQueue("greeting-queue")` must also be set on the activity stub to route activity tasks to the correct queue.

### Comparison: Auto-Discovery vs Explicit YAML Registration

Auto-discovery via annotations:
```properties
spring.temporal.workersAutoDiscovery.packages=greetingapp
```
```java
@Component
@ActivityImpl(taskQueues = "greeting-queue")
public class GreetActivitiesImpl implements GreetActivities { ... }
```

Explicit YAML registration (alternative):
```yaml
spring:
  temporal:
    workers:
      - task-queue: greeting-queue
        name: greeting-worker
        activity-beans:
          - greetActivitiesImpl
        workflow-classes:
          - greetingapp.GreetingWorkflowImpl
```

Use auto-discovery when implementations are colocated in a single package tree (most apps). Use explicit YAML when you need fine-grained control, want to exclude specific classes, or are registering beans defined elsewhere.

## WorkflowClient Injection

`WorkflowClient` is automatically registered as a Spring bean by the autoconfigure. Inject it into any `@Service` or `@RestController`:

```java
package greetingapp;

import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class GreetingStarter {

    private final WorkflowClient client;

    public GreetingStarter(WorkflowClient client) {
        this.client = client;
    }

    public String startGreeting(String name) {
        var stub = client.newWorkflowStub(
            GreetingWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId(UUID.randomUUID().toString())
                .setTaskQueue("greeting-queue")  // must match the worker's task queue
                .build()
        );
        // Synchronous — blocks until workflow completes
        return stub.greet(name);
    }

    public void startGreetingAsync(String name) {
        var stub = client.newWorkflowStub(
            GreetingWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId(UUID.randomUUID().toString())
                .setTaskQueue("greeting-queue")
                .build()
        );
        // Fire-and-forget — returns immediately
        WorkflowClient.start(stub::greet, name);
    }
}
```

## Worker Lifecycle

Workers start on `ApplicationReadyEvent` — after the full Spring context is initialized (DB migrations run, all beans wired). This means activity beans are fully ready before any workflow tasks are processed.

To run a client-only app (one that submits workflows but does not execute them):
```properties
spring.temporal.start-workers=false
```

## Testing Strategies

See `references/java/testing.md` for full details on both approaches.

**Spring integration tests** — uses an embedded Temporal test server wired into the Spring context:
```properties
# src/test/resources/application-test.properties
spring.temporal.test-server.enabled=true
```
```java
@SpringBootTest
@ActiveProfiles("test")
class GreetingIntegrationTest {
    @Autowired WorkflowClient client;  // points at the embedded test server

    @Test
    void testWorkflowThroughSpringContext() { ... }
}
```

**Unit tests without Spring** — use `TestWorkflowEnvironment` or `TestWorkflowExtension` directly. No Spring context, faster startup, full time-skipping support:
```java
@RegisterExtension
static final TestWorkflowExtension testWorkflow = TestWorkflowExtension.newBuilder()
    .setWorkflowTypes(GreetingWorkflowImpl.class)
    .setDoNotStart(true)
    .build();
```

Do not mix approaches in the same test class — choose one or the other.

## Spring-Specific Gotchas

**Workflow impls must not have `@Component`**
Temporal creates a new workflow instance per execution via `beanFactory.createBean()` (not `getBean()`). Adding `@Component` means Spring also registers it as a singleton bean, which can cause confusing lifecycle behavior. Leave `@WorkflowImpl` classes as plain classes with no Spring annotations.

**Activity beans are Spring singletons**
Temporal may invoke activity methods concurrently across many workflow executions. Keep activity implementations stateless — no mutable instance fields. Use injected services (which are themselves stateless or thread-safe) for all state.

**`@WorkflowImpl` / `@ActivityImpl` without `workersAutoDiscovery.packages` → silently ignored**
This is the most common setup mistake. If auto-discovery packages are not configured, the annotations are never scanned and nothing registers with the worker. Verify with the Temporal UI that the worker is registering the expected workflow/activity types.

**`ActivityOptions.setTaskQueue(...)` is required on activity stubs**
`@ActivityImpl(taskQueues = "greeting-queue")` registers the activity bean with the worker — it does not set the default task queue for activity execution. Inside workflow code, always set `.setTaskQueue(...)` in `ActivityOptions` to explicitly route activity tasks to the correct worker.

**Multiple `DataConverter` beans**
If you define more than one `DataConverter` bean (e.g., a custom JSON converter and a default), the autoconfigure fails with an ambiguity error. Name one of them `mainDataConverter` to designate it as the primary.
