# Compatible image and speech APIs

Checked on 2026-11-15 against the [OpenAI image API](https://developers.openai.com/api/reference/resources/images) and [speech API](https://developers.openai.com/api/reference/resources/audio/subresources/speech/methods/create). Compatibility depends on the selected provider implementing these contracts; a provider preset is not certification of every model or endpoint.

Configure a public HTTPS API base URL, protocol and key in **Settings → Model providers**. Keep the documented version/path prefix, such as `/v1`. The local service stores the key privately and injects `Authorization: Bearer …`; never read it or pass it to the Tool. User-configurable URLs retain public DNS validation and do not follow authenticated redirects. Localhost/private-network services require a dedicated integration.

Call `openmotion_media_use` with `action=inspect` to obtain the actual provider ID (custom IDs start with `custom-`). Read this reference, then call `action=models`, `provider=<that ID>`, `refresh=true`. Discovery uses `GET <base>/models` and reads `data[].id`; explicit output metadata establishes image/audio capability. Unknown models remain language models. In settings, add a model with its exact ID and Image or Audio capability when the provider's documentation confirms that operation. Language and embedding defaults are configuration for Agent integrations, not media generation.

Image request template (replace placeholders with discovered IDs):

```json
{"action":"generate","projectId":"PROJECT_ID","provider":"PROVIDER_ID","model":"MODEL_ID","requestId":"image-one","modality":"image","prompt":"A ceramic cup","parameters":{"size":"1024x1024"}}
```

The wire request is `POST <base>/images/generations` with JSON `{model,prompt,...parameters}`. Read the selected model's supported parameters first. Returned `data[].b64_json` or `data[].url` becomes validated project-owned media. This adapter does not implement an image-edit upload protocol or asynchronous video endpoints.

Speech request template:

```json
{"action":"generate","projectId":"PROJECT_ID","provider":"PROVIDER_ID","model":"MODEL_ID","requestId":"speech-one","modality":"audio","mode":"text-to-speech","prompt":"Welcome to the studio.","parameters":{"voice":"PROVIDER_VOICE_ID"}}
```

The wire request is `POST <base>/audio/speech` with JSON `{model,input:prompt,voice,...parameters}` and binary audio output. Voice is required; music, transcription and sound-effects protocols are not implemented by this adapter.

The Tool returns a local queued job. Poll `action=status` with the original projectId/jobId until completion. A successful synchronous provider response has no separate remote task ID. Stable requestId prevents duplicate local submission. HTTP 401/403 means authorization or permissions were rejected; 400/422 needs a model/input correction; 429 means rate/quota limits; 5xx or timeout can have an uncertain paid outcome. Raw upstream bodies and keys are not exposed. No error automatically resubmits, changes model or changes provider. Local cancel cannot establish remote cancellation or refund; inspect provider history before intentionally retrying.
