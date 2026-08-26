# Java SDK Testing

## Overview

You test Temporal Java Workflows using `TestWorkflowEnvironment` (manual setup) or `TestWorkflowExtension` (JUnit 5). Activity mocking uses Mockito. The SDK provides `WorkflowReplayer` for replay-based compatibility testing.

## Workflow Test Environment

```java
import io.temporal.testing.TestWorkflowExtension;
import io.temporal.testing.TestWorkflowEnvironment;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowOptions;
import io.temporal.worker.Worker;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class MyWorkflowTest {

    @RegisterExtension
    public static final TestWorkflowExtension testWorkflowExtension =
        TestWorkflowExtension.newBuilder()
            .setWorkflowTypes(MyWorkflowImpl.class)
            .setDoNotStart(true)
            .build();

    @Test
    void testWorkflow(TestWorkflowEnvironment env, Worker worker, WorkflowClient client) {
        worker.registerActivitiesImplementations(new MyActivitiesImpl());
        env.start();

        MyWorkflow workflow = client.newWorkflowStub(
            MyWorkflow.class,
            WorkflowOptions.newBuilder()
                .setTaskQueue(worker.getTaskQueue())
                .build());

        String result = workflow.run("input");
        assertEquals("expected", result);
    }
}
```

For manual lifecycle control (e.g., JUnit 4 or custom setups), use `TestWorkflowEnvironment` directly with `@BeforeEach`/`@AfterEach`.

## Mocking Activities

```java
import static org.mockito.Mockito.*;

@Test
void testWithMockedActivities(
        TestWorkflowEnvironment env,
        Worker worker,
        WorkflowClient client) {
    // withoutAnnotations() prevents Mockito from copying Temporal annotations
    MyActivities activities = mock(MyActivities.class, withSettings().withoutAnnotations());
    when(activities.composeGreeting("Hello", "World")).thenReturn("mocked result");

    worker.registerActivitiesImplementations(activities);
    env.start();

    MyWorkflow workflow = client.newWorkflowStub(
        MyWorkflow.class,
        WorkflowOptions.newBuilder()
            .setTaskQueue(worker.getTaskQueue())
            .build());

    String result = workflow.run("input");
    assertEquals("mocked result", result);
    verify(activities).composeGreeting("Hello", "World");
}
```

## Testing Signals and Queries

```java
@Test
void testSignalsAndQueries(
        TestWorkflowEnvironment env,
        Worker worker,
        WorkflowClient client) {
    worker.registerActivitiesImplementations(new MyActivitiesImpl());
    env.start();

    MyWorkflow workflow = client.newWorkflowStub(
        MyWorkflow.class,
        WorkflowOptions.newBuilder()
            .setTaskQueue(worker.getTaskQueue())
            .build());

    // Start workflow asynchronously
    WorkflowClient.start(workflow::run, "input");

    // Send signal
    workflow.mySignal("data");

    // Query state
    String status = workflow.getStatus();
    assertEquals("expected", status);

    // Wait for completion
    String result = WorkflowStub.fromTyped(workflow).getResult(String.class);
}
```

## Testing Failure Cases

```java
import io.temporal.client.WorkflowException;

@Test
void testActivityFailure(
        TestWorkflowEnvironment env,
        Worker worker,
        WorkflowClient client) {
    MyActivities activities = mock(MyActivities.class, withSettings().withoutAnnotations());
    when(activities.unreliableAction(anyString()))
        .thenThrow(new RuntimeException("Simulated failure"));

    worker.registerActivitiesImplementations(activities);
    env.start();

    MyWorkflow workflow = client.newWorkflowStub(
        MyWorkflow.class,
        WorkflowOptions.newBuilder()
            .setTaskQueue(worker.getTaskQueue())
            .build());

    assertThrows(WorkflowException.class, () -> workflow.run("input"));
}
```

## Workflow Replay Testing

```java
import io.temporal.testing.WorkflowReplayer;

@Test
void testReplayFromHistory() throws Exception {
    WorkflowReplayer.replayWorkflowExecutionFromResource(
        "my-workflow-history.json",
        MyWorkflowImpl.class);
}
```

Replay from a `WorkflowHistory` object:

```java
import io.temporal.common.WorkflowExecutionHistory;

@Test
void testReplayFromJsonString() throws Exception {
    String historyJson = new String(Files.readAllBytes(Paths.get("history.json")));
    WorkflowReplayer.replayWorkflowExecution(
        WorkflowExecutionHistory.fromJson(historyJson),
        MyWorkflowImpl.class);
}
```

## Activity Testing

Activity implementations are plain Java classes. Test them directly:

```java
@Test
void testActivity() {
    MyActivitiesImpl activities = new MyActivitiesImpl();
    String result = activities.composeGreeting("Hello", "World");
    assertEquals("Hello World", result);
}
```

For activities that use `Activity.getExecutionContext()` or heartbeating, use `TestActivityEnvironment` to provide the activity context.

## Best Practices

1. Use `TestWorkflowExtension` with JUnit 5 for concise test setup
2. Always use `withSettings().withoutAnnotations()` when mocking activity interfaces with Mockito
3. Mock external dependencies in activities, not in workflows
4. Test replay compatibility when changing workflow code (see `references/java/determinism.md`)
5. Test signal/query handlers explicitly
6. Use unique task queues per test to avoid conflicts (handled automatically by `TestWorkflowExtension`)

## Spring Boot Testing

Two strategies — choose one per test class, do not mix them.

### Embedded test server in Spring context

For full integration tests that exercise the Spring context (DB, beans, config):

```properties
# src/test/resources/application-test.properties
spring.temporal.test-server.enabled=true
```

```java
@SpringBootTest
@ActiveProfiles("test")
class TeeTimeMonitorIntegrationTest {

    @Autowired
    WorkflowClient client;  // auto-configured to point at the embedded test server

    @Test
    void testWorkflow() {
        var stub = client.newWorkflowStub(
            TeeTimeMonitorWorkflow.class,
            WorkflowOptions.newBuilder()
                .setWorkflowId("test-" + UUID.randomUUID())
                .setTaskQueue("golfnow")
                .build()
        );
        var result = stub.monitorTeeTimes(new TTMonitorRequest(...));
        assertNotNull(result);
    }
}
```

The embedded server does not support time-skipping. Use this when you need Spring beans (real DB, email service, etc.) wired alongside Temporal.

### Unit tests without Spring context

For faster, isolated tests with time-skipping support, use `TestWorkflowExtension` or `TestWorkflowEnvironment` directly. No Spring context starts, so activity dependencies must be provided manually (real instances or Mockito mocks):

```java
public class TeeTimeMonitorWorkflowTest {

    @RegisterExtension
    static final TestWorkflowExtension testWorkflow = TestWorkflowExtension.newBuilder()
        .setWorkflowTypes(TeeTimeMonitorWorkflowImpl.class)
        .setDoNotStart(true)
        .build();

    @Test
    void testWorkflow(TestWorkflowEnvironment env, Worker worker, WorkflowClient client) {
        GolfNowActivities activities = mock(GolfNowActivities.class, withSettings().withoutAnnotations());
        when(activities.searchTeeTimes(any())).thenReturn(List.of());

        worker.registerActivitiesImplementations(activities);
        env.start();

        var stub = client.newWorkflowStub(
            TeeTimeMonitorWorkflow.class,
            WorkflowOptions.newBuilder().setTaskQueue(worker.getTaskQueue()).build()
        );
        stub.monitorTeeTimes(new TTMonitorRequest(...));
        verify(activities).searchTeeTimes(any());
    }
}
```

See the sections above for more detail on mocking, signals/queries, and replay testing.
