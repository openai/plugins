# Ruby SDK Testing

## Overview

The Temporal Ruby SDK provides testing utilities compatible with any Ruby test framework (minitest is commonly used). The two main testing classes are `Temporalio::Testing::WorkflowEnvironment` for end-to-end workflow testing and `Temporalio::Testing::ActivityEnvironment` for isolated activity testing.

## Workflow Test Environment

The core pattern:
1. Start a test `WorkflowEnvironment` with `start_local`
2. Create a Worker in that environment with your Workflows and Activities registered
3. Execute the Workflow using the environment's client
4. Assert on the result

```ruby
require 'minitest/autorun'
require 'securerandom'
require 'temporalio/testing/workflow_environment'
require 'temporalio/worker'

require_relative '../workflows/my_workflow'
require_relative '../activities/my_activity'

class MyWorkflowTest < Minitest::Test
  def test_workflow_returns_expected_result
    Temporalio::Testing::WorkflowEnvironment.start_local do |env|
      task_queue = SecureRandom.uuid

      worker = Temporalio::Worker.new(
        client: env.client,
        task_queue: task_queue,
        workflows: [MyWorkflow],
        activities: [MyActivity]
      )

      worker.run do
        result = env.client.execute_workflow(
          MyWorkflow,
          'input-arg',
          id: SecureRandom.uuid,
          task_queue: task_queue
        )

        assert_equal 'expected output', result
      end
    end
  end
end
```

For workflows with long durations (timers, sleeps), use `start_time_skipping` instead of `start_local`:

```ruby
Temporalio::Testing::WorkflowEnvironment.start_time_skipping do |env|
  # Timers are automatically skipped
end
```

## Mocking Activities

Create fake activity classes with the same activity name as the real ones. Pass them to the Worker instead of the real activities:

```ruby
class FakeComposeGreetingActivity < Temporalio::Activity::Definition
  activity_name 'ComposeGreetingActivity'

  def execute(input)
    'mocked greeting'
  end
end

class MyWorkflowMockTest < Minitest::Test
  def test_workflow_with_mocked_activity
    Temporalio::Testing::WorkflowEnvironment.start_local do |env|
      task_queue = SecureRandom.uuid

      worker = Temporalio::Worker.new(
        client: env.client,
        task_queue: task_queue,
        workflows: [MyWorkflow],
        activities: [FakeComposeGreetingActivity]
      )

      worker.run do
        result = env.client.execute_workflow(
          MyWorkflow,
          'test-input',
          id: SecureRandom.uuid,
          task_queue: task_queue
        )

        assert_equal 'mocked greeting', result
      end
    end
  end
end
```

## Testing Signals and Queries

Use `start_workflow` to get a handle, then interact via signal/query methods:

```ruby
class SignalQueryTest < Minitest::Test
  def test_signal_and_query
    Temporalio::Testing::WorkflowEnvironment.start_local do |env|
      task_queue = SecureRandom.uuid

      worker = Temporalio::Worker.new(
        client: env.client,
        task_queue: task_queue,
        workflows: [MyWorkflow],
        activities: [MyActivity]
      )

      worker.run do
        handle = env.client.start_workflow(
          MyWorkflow,
          id: SecureRandom.uuid,
          task_queue: task_queue
        )

        # Send a signal
        handle.signal(MyWorkflow.my_signal, 'signal-data')

        # Query workflow state
        status = handle.query(MyWorkflow.get_status)
        assert_equal 'expected-status', status

        # Wait for completion
        result = handle.result
        assert_equal 'done', result
      end
    end
  end
end
```

## Testing Failure Cases

Test workflows that encounter errors using activities that raise exceptions:

```ruby
class FailingActivity < Temporalio::Activity::Definition
  activity_name 'MyActivity'

  def execute(input)
    raise Temporalio::Error::ApplicationError.new('Simulated failure', non_retryable: true)
  end
end

class FailureTest < Minitest::Test
  def test_workflow_handles_activity_failure
    Temporalio::Testing::WorkflowEnvironment.start_local do |env|
      task_queue = SecureRandom.uuid

      worker = Temporalio::Worker.new(
        client: env.client,
        task_queue: task_queue,
        workflows: [MyWorkflow],
        activities: [FailingActivity]
      )

      worker.run do
        assert_raises(Temporalio::Error::WorkflowFailureError) do
          env.client.execute_workflow(
            MyWorkflow,
            'input',
            id: SecureRandom.uuid,
            task_queue: task_queue
          )
        end
      end
    end
  end
end
```

## Workflow Replay Testing

Use `WorkflowReplayer` to verify that workflow code changes remain compatible with existing histories:

```ruby
require 'temporalio/worker/workflow_replayer'
require 'temporalio/workflow_history'

class ReplayTest < Minitest::Test
  def test_replay_from_json
    json = File.read('test/fixtures/my_workflow_history.json')
    replayer = Temporalio::Worker::WorkflowReplayer.new(workflows: [MyWorkflow])

    # Replay a single workflow history
    replayer.replay_workflow(
      Temporalio::WorkflowHistory.from_history_json(json)
    )
  end

  def test_replay_bulk
    histories = Dir['test/fixtures/histories/*.json'].map do |path|
      Temporalio::WorkflowHistory.from_history_json(File.read(path))
    end

    replayer = Temporalio::Worker::WorkflowReplayer.new(workflows: [MyWorkflow])

    # Replay multiple histories - raises on nondeterminism
    replayer.replay_workflows(histories)
  end
end
```

## Activity Testing

Use `ActivityEnvironment` to test activities in isolation without a full Temporal server:

```ruby
require 'temporalio/testing/activity_environment'

class ActivityTest < Minitest::Test
  def test_activity_returns_greeting
    env = Temporalio::Testing::ActivityEnvironment.new
    result = env.run(MyActivity, 'World')
    assert_equal 'Hello, World!', result
  end
end
```

## Best Practices

1. **Use `start_local` for most tests** - provides a real Temporal environment without external dependencies
2. **Use `start_time_skipping` for timer tests** - automatically skips timers rather than waiting
3. **Mock external dependencies** - create fake activity classes with `activity_name` matching the real activity
4. **Test replay compatibility** - add replay tests when changing workflow code to catch nondeterminism errors early
5. **Use unique IDs per test** - use `SecureRandom.uuid` for workflow IDs and task queue names to avoid conflicts
6. **Test signals and queries explicitly** - use `start_workflow` to get a handle rather than `execute_workflow`
