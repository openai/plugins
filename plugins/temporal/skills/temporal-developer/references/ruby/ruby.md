# Temporal Ruby SDK Reference

## Overview

The Temporal Ruby SDK (`temporalio` gem) provides a class-based approach to building durable workflows. Ruby 3.3+ required. Workflows run using a Durable Fiber Scheduler for determinism protection, with Illegal Call Tracing via `TracePoint` to detect non-deterministic operations.

## Quick Demo of Temporal

**Add Dependency on Temporal:** Add `temporalio` to your Gemfile or install directly with `gem install temporalio`.

**say_hello_activity.rb** - Activity definition:
```ruby
require 'temporalio/activity'

class SayHelloActivity < Temporalio::Activity::Definition
  def execute(name)
    "Hello, #{name}!"
  end
end
```

**say_hello_workflow.rb** - Workflow definition:
```ruby
require 'temporalio/workflow'

class SayHelloWorkflow < Temporalio::Workflow::Definition
  def execute(name)
    Temporalio::Workflow.execute_activity(
      SayHelloActivity,
      name,
      schedule_to_close_timeout: 30
    )
  end
end
```

**worker.rb** - Worker setup (imports activity and workflow, runs indefinitely and processes tasks):
```ruby
require 'temporalio/client'
require 'temporalio/env_config'
require 'temporalio/worker'
require_relative 'say_hello_activity'
require_relative 'say_hello_workflow'

args, kwargs = Temporalio::EnvConfig::ClientConfig.load_client_connect_options
args[0] ||= 'localhost:7233'
args[1] ||= 'default'
client = Temporalio::Client.connect(*args, **kwargs)

# Create and run the worker
worker = Temporalio::Worker.new(
  client: client,
  task_queue: 'my-task-queue',
  workflows: [SayHelloWorkflow],
  activities: [SayHelloActivity]
)
worker.run
```

**Start the dev server:** Start `temporal server start-dev` in the background.

**Start the worker:** Start `ruby worker.rb` in the background.

**execute_workflow.rb** - Start a workflow execution:
```ruby
require 'temporalio/client'
require 'temporalio/env_config'
require 'securerandom'
require_relative 'say_hello_workflow'

args, kwargs = Temporalio::EnvConfig::ClientConfig.load_client_connect_options
args[0] ||= 'localhost:7233'
args[1] ||= 'default'
client = Temporalio::Client.connect(*args, **kwargs)

# Execute a workflow
result = client.execute_workflow(
  SayHelloWorkflow,
  'my name',
  id: SecureRandom.uuid,
  task_queue: 'my-task-queue'
)

puts "Result: #{result}"
```

**Run the workflow:** Run `ruby execute_workflow.rb`. Should output: `Result: Hello, my name!`.

## Key Concepts

### Workflow Definition
- Subclass `Temporalio::Workflow::Definition`
- Define `def execute(args)` as the entry point
- Use `Temporalio::Workflow.execute_activity` to call activities
- Define signals, queries, and updates via class-level DSL methods

### Activity Definition
- Subclass `Temporalio::Activity::Definition`
- Define `def execute(args)` as the entry point
- Activities contain all non-deterministic and side-effectful code
- Can access `Temporalio::Activity::Context.current` for heartbeating

### Worker Setup
- Load connection settings with `Temporalio::EnvConfig::ClientConfig.load_client_connect_options` and connect with `Temporalio::Client.connect`
- Create worker with `Temporalio::Worker.new(client:, task_queue:, workflows:, activities:)`
- Run with `worker.run`

### Determinism

**Workflow code must be deterministic!** The Ruby SDK uses a Durable Fiber Scheduler and Illegal Call Tracing (via Ruby's `TracePoint`) to detect non-deterministic operations at runtime. All sources of non-determinism should either use Temporal-provided alternatives or be defined in Activities. Read `references/core/determinism.md` and `references/ruby/determinism.md` to understand more.

## File Organization Best Practice

**Keep Workflow definitions in separate files from Activity definitions.** Unlike Python, Ruby does not have a sandbox reloading concern, but separating workflows and activities is still good practice for clarity and maintainability. Use `require_relative` to import between files.

```
my_temporal_app/
├── workflows/
│   └── say_hello_workflow.rb   # Only Workflow classes
├── activities/
│   └── say_hello_activity.rb   # Only Activity classes
├── worker.rb                   # Worker setup, requires both
└── execute_workflow.rb          # Client code to start workflows
```

## Common Pitfalls

1. **Using `sleep` instead of `Temporalio::Workflow.sleep`** - Standard `sleep` is non-deterministic and will be flagged by Illegal Call Tracing; use the Temporal-provided version
2. **Using `Time.now` instead of `Temporalio::Workflow.now`** - Same issue; `Time.now` is non-deterministic in workflow context
3. **Third-party gems triggering illegal calls** - Gems that perform I/O, use threads, or call system time will be caught by `TracePoint` tracing; move that logic to activities
4. **Using `puts`/`Logger` in workflows** - Use `Temporalio::Workflow.logger` instead for replay-safe logging
5. **Not heartbeating long activities** - Long-running activities need `Temporalio::Activity::Context.current.heartbeat`
6. **Mixing Workflows and Activities in same file** - Bad structure; keep them separated for clarity

## Writing Tests

See `references/ruby/testing.md` for info on writing tests.

## Additional Resources

### Reference Files
- **`references/ruby/patterns.md`** - Signals, queries, child workflows, saga pattern, etc.
- **`references/ruby/determinism.md`** - Durable Fiber Scheduler behavior, safe alternatives, history replay
- **`references/ruby/determinism-protection.md`** - Illegal Call Tracing via TracePoint, forbidden operations, runtime detection
- **`references/ruby/versioning.md`** - Patching API, workflow type versioning, Worker Versioning
- **`references/ruby/testing.md`** - Test environments, time-skipping, activity mocking
- **`references/ruby/error-handling.md`** - ApplicationError, retry policies, non-retryable errors, idempotency
- **`references/ruby/data-handling.md`** - Data converters, payload encryption
- **`references/ruby/observability.md`** - Logging, metrics, tracing, Search Attributes
- **`references/ruby/gotchas.md`** - Ruby-specific mistakes and anti-patterns
- **`references/ruby/advanced-features.md`** - Schedules, worker tuning, and more
