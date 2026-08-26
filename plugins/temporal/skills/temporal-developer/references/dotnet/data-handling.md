# .NET SDK Data Handling

## Overview

The .NET SDK uses data converters to serialize/deserialize workflow inputs, outputs, and activity parameters.

## Default Data Converter

The default converter handles:

- `null`
- `byte[]` (as binary)
- `Google.Protobuf.IMessage` instances
- Anything that `System.Text.Json` supports
- `IRawValue` as unconverted raw payloads

## Custom Data Converter

Customize serialization by extending `DefaultPayloadConverter`. For example, to use camelCase property naming:

```csharp
using System.Text.Json;
using Temporalio.Client;
using Temporalio.Converters;

public class CamelCasePayloadConverter : DefaultPayloadConverter
{
    public CamelCasePayloadConverter()
        : base(new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })
    {
    }
}

var client = await TemporalClient.ConnectAsync(new()
{
    TargetHost = "localhost:7233",
    Namespace = "my-namespace",
    DataConverter = DataConverter.Default with
    {
        PayloadConverter = new CamelCasePayloadConverter(),
    },
});
```

## Protobuf Support

The default data converter includes built-in support for Protocol Buffer messages via `Google.Protobuf.IMessage`. Protobuf messages are automatically serialized using proto3 JSON.

```csharp
// Any Google.Protobuf.IMessage is automatically handled
[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<MyProtoResponse> RunAsync(MyProtoRequest request)
    {
        // Protobuf messages are serialized/deserialized automatically
        return await Workflow.ExecuteActivityAsync(
            (MyActivities a) => a.ProcessAsync(request),
            new() { StartToCloseTimeout = TimeSpan.FromMinutes(5) });
    }
}
```

## Payload Encryption

Encrypt sensitive workflow data using a custom `IPayloadCodec`:

```csharp
using Temporalio.Converters;
using Google.Protobuf;

public class EncryptionCodec : IPayloadCodec
{
    public Task<IReadOnlyCollection<Payload>> EncodeAsync(
        IReadOnlyCollection<Payload> payloads) =>
        Task.FromResult<IReadOnlyCollection<Payload>>(payloads.Select(p =>
            new Payload
            {
                Metadata = { ["encoding"] = "binary/encrypted" },
                Data = ByteString.CopyFrom(Encrypt(p.ToByteArray())),
            }).ToList());

    public Task<IReadOnlyCollection<Payload>> DecodeAsync(
        IReadOnlyCollection<Payload> payloads) =>
        Task.FromResult<IReadOnlyCollection<Payload>>(payloads.Select(p =>
        {
            if (p.Metadata.GetValueOrDefault("encoding") != "binary/encrypted")
                return p;
            return Payload.Parser.ParseFrom(Decrypt(p.Data.ToByteArray()));
        }).ToList());

    private byte[] Encrypt(byte[] data) => /* your encryption logic */;
    private byte[] Decrypt(byte[] data) => /* your decryption logic */;
}

// Apply encryption codec
var client = await TemporalClient.ConnectAsync(new("localhost:7233")
{
    DataConverter = DataConverter.Default with
    {
        PayloadCodec = new EncryptionCodec(),
    },
});
```

## Search Attributes

Custom searchable fields for workflow visibility. These can be set at workflow start:

```csharp
using Temporalio.Common;

var handle = await client.StartWorkflowAsync(
    (OrderWorkflow wf) => wf.RunAsync(order),
    new(id: $"order-{order.Id}", taskQueue: "orders")
    {
        TypedSearchAttributes = new SearchAttributeCollection.Builder()
            .Set(SearchAttributeKey.CreateKeyword("OrderId"), order.Id)
            .Set(SearchAttributeKey.CreateKeyword("OrderStatus"), "pending")
            .Set(SearchAttributeKey.CreateFloat("OrderTotal"), order.Total)
            .Build(),
    });
```

Or upserted during workflow execution:

```csharp
[Workflow]
public class OrderWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        // ... process order ...

        // Update search attribute
        Workflow.UpsertTypedSearchAttributes(
            SearchAttributeKey.CreateKeyword("OrderStatus").ValueSet("completed"));
        return "done";
    }
}
```

### Querying Workflows by Search Attributes

```csharp
await foreach (var wf in client.ListWorkflowsAsync(
    "OrderStatus = \"processing\" OR OrderStatus = \"pending\""))
{
    Console.WriteLine($"Workflow {wf.Id} is still processing");
}
```

## Workflow Memo

Store arbitrary metadata with workflows (not searchable).

```csharp
await client.ExecuteWorkflowAsync(
    (OrderWorkflow wf) => wf.RunAsync(order),
    new(id: $"order-{order.Id}", taskQueue: "orders")
    {
        Memo = new Dictionary<string, object>
        {
            ["customer_name"] = order.CustomerName,
            ["notes"] = "Priority customer",
        },
    });
```

```csharp
// Read memo from workflow
[Workflow]
public class OrderWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync(Order order)
    {
        var notes = Workflow.Memo["notes"];
        // ...
    }
}
```

## Deterministic APIs for Values

Use these APIs within workflows for deterministic random values and UUIDs:

```csharp
[Workflow]
public class MyWorkflow
{
    [WorkflowRun]
    public async Task<string> RunAsync()
    {
        // Deterministic GUID (same on replay)
        var uniqueId = Workflow.NewGuid();

        // Deterministic random (same on replay)
        var value = Workflow.Random.Next(1, 100);

        // Deterministic current time
        var now = Workflow.UtcNow;

        return uniqueId.ToString();
    }
}
```

## Best Practices

1. Use records or classes with `System.Text.Json` support for input/output
2. Keep payloads small — see `references/core/gotchas.md` for limits
3. Encrypt sensitive data with `IPayloadCodec`
4. Use `Workflow.NewGuid()` and `Workflow.Random` for deterministic values
5. Use camelCase converter if interoperating with other SDKs
