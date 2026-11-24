# Workers AI API

Fetch the selected model's page from the [model catalog](https://developers.cloudflare.com/workers-ai/models/index.md) for request fields, output format, dimensions, and examples. Text, embeddings, images, audio, and translation do not share one response schema.

| Task | Documentation |
|------|---------------|
| Invoke inference through a Worker binding | [Workers bindings](https://developers.cloudflare.com/workers-ai/configuration/bindings/index.md) |
| Invoke inference over HTTP | [REST API reference](https://developers.cloudflare.com/api/resources/ai/methods/run/index.md) |
| Stream text or use SDK abstractions | [Vercel AI SDK](https://developers.cloudflare.com/workers-ai/configuration/ai-sdk/index.md), or the selected model's streaming example |
| Define tools and handle tool results | [Function calling](https://developers.cloudflare.com/workers-ai/features/function-calling/index.md) |
| Request structured output | [JSON mode](https://developers.cloudflare.com/workers-ai/features/json-mode/index.md) |

Use the response and stream format documented for the chosen integration. Do not assume native binding streams are parsed objects or apply OpenAI response parsing to every model. Check the model's batching support and limits before combining inputs in one request.
