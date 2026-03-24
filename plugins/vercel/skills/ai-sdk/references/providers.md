# AI SDK — Provider Reference

## Global Provider System

Use `"provider/model"` format for automatic AI Gateway routing:

```ts
import { gateway } from 'ai'
const model = gateway('openai/gpt-5.2')
```

## Provider Packages

| Provider | Package | Example Models |
|----------|---------|---------------|
| OpenAI | `@ai-sdk/openai` | `gpt-5.2`, `gpt-5.1-instant`, `gpt-5-nano`, `gpt-5.3-codex`, `o3` |
| Anthropic | `@ai-sdk/anthropic` | `claude-opus-4.6`, `claude-sonnet-4.6`, `claude-haiku-4.5` |
| Google | `@ai-sdk/google` | `gemini-3.1-pro-preview`, `gemini-3-flash`, `gemini-3.1-flash` |
| xAI | `@ai-sdk/xai` | `grok-4.1` |
| Mistral | `@ai-sdk/mistral` | `mistral-large`, `mistral-small` |
| Cohere | `@ai-sdk/cohere` | `command-r-plus`, `rerank-v3.5` |
| Amazon Bedrock | `@ai-sdk/amazon-bedrock` | All Bedrock models |
| Azure OpenAI | `@ai-sdk/azure` | Azure-hosted OpenAI models |
| DeepSeek | `@ai-sdk/deepseek` | `deepseek-r1`, `deepseek-v3` |
| Perplexity | `@ai-sdk/perplexity` | `sonar-pro`, `sonar` |
| AI Gateway | `@ai-sdk/gateway` | Routes to any provider |

## Model Selection Guide

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Fast chat responses | `gpt-5-nano`, `gemini-3-flash`, `claude-haiku-4.5` | Low latency, low cost |
| General purpose | `gpt-5.2`, `claude-sonnet-4.6`, `gemini-3-flash` | Best quality/speed balance |
| Complex reasoning | `claude-opus-4.6`, `gpt-5.2`, `gemini-3.1-pro-preview` | Best reasoning |
| Code generation | `gpt-5.3-codex`, `claude-sonnet-4.6` | Code-optimized |
| Embeddings | `text-embedding-3-small` (OpenAI) | Cost-effective, good quality |
| Embeddings (high-quality) | `text-embedding-3-large` (OpenAI) | Best quality |
| Image generation | `google/gemini-3.1-flash-image-preview` (via gateway) | Fast, high-quality multimodal image gen |
| Reranking | `rerank-v3.5` (Cohere) | Relevance reordering |

## Direct Provider Usage

```ts
import { openai } from '@ai-sdk/openai'
import { anthropic } from '@ai-sdk/anthropic'
import { google } from '@ai-sdk/google'

// Text models
const gpt = openai('gpt-5.2')
const claude = anthropic('claude-sonnet-4.6')
const gemini = google('gemini-3-flash')

// Embedding models
const embedder = openai.embedding('text-embedding-3-small')

// Image models (use gateway for image gen)
// const imageGen = gateway('google/gemini-3.1-flash-image-preview')
```
