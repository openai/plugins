# Higgsfield

Higgsfield brings AI image and video creation workflows into Codex through the hosted Higgsfield MCP server for OpenAI clients.

Use this plugin to generate images and videos, inspect generation jobs, manage uploaded media, open marketing asset workflows, work with character tools, view billing and credits, and analyze videos with Virality Predictor.

## MCP Server

```json
{
  "mcpServers": {
    "higgsfield": {
      "type": "http",
      "url": "https://openai-mcp.higgsfield.ai/mcp",
      "note": "Higgsfield AI MCP server for OpenAI/Codex clients. Uses authenticated Higgsfield access and provides tools for image/video generation, media and job workflows, marketing assets."
    }
  }
}
```

The OpenAI/Codex MCP endpoint requires authenticated Higgsfield access on first use.

## Common Workflows

- Generate images from text prompts and model-specific settings.
- Generate videos from prompts, images, characters, and references.
- Check generation status and display completed jobs.
- Upload, confirm, and reuse media assets.
- Create marketing assets through Higgsfield's Marketing Studio tools.
- Analyze video virality, attention, and retention signals with Virality Predictor.
- View plan, credit, balance, transaction, and workspace information.

## Authentication

Higgsfield uses authenticated access for account-specific workflows such as generation, media, jobs, billing, workspaces, and character tools. Codex will handle the MCP connection flow when the plugin is installed or first used.

## Links

- Website: https://higgsfield.ai
- Privacy Policy: https://higgsfield.ai/privacy-policy
- Terms of Use: https://higgsfield.ai/terms-of-use-agreement
