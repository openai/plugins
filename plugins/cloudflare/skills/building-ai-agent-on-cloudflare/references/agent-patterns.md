# Agent Patterns

Advanced patterns for building sophisticated agents.

## Tool Calling

Agents can expose tools that AI models can call:

```typescript
import { Agent, Connection } from "agents";
import { z } from "zod";

interface Tool {
  name: string;
  description: string;
  parameters: z.ZodSchema;
  handler: (params: any) => Promise<string>;
}

export class ToolAgent extends Agent<Env, State> {
  private tools: Map<string, Tool> = new Map();

  async onStart() {
    // Register tools
    this.registerTool({
      name: "get_weather",
      description: "Get current weather for a city",
      parameters: z.object({ city: z.string() }),
      handler: async ({ city }) => {
        const res = await fetch(`https://api.weather.com/${city}`);
        return JSON.stringify(await res.json());
      },
    });

    this.registerTool({
      name: "search_database",
      description: "Search the document database",
      parameters: z.object({ query: z.string(), limit: z.number().default(10) }),
      handler: async ({ query, limit }) => {
        const results = await this.sql`
          SELECT * FROM documents
          WHERE content LIKE ${`%${query}%`}
          LIMIT ${limit}
        `;
        return JSON.stringify(results);
      },
    });
  }

  private registerTool(tool: Tool) {
    this.tools.set(tool.name, tool);
  }

  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      await this.handleChatWithTools(connection, data.content);
    }
  }

  private async handleChatWithTools(connection: Connection, userMessage: string) {
    // Build tool descriptions for the AI
    const toolDescriptions = Array.from(this.tools.values()).map((t) => ({
      type: "function",
      function: {
        name: t.name,
        description: t.description,
        parameters: JSON.parse(JSON.stringify(t.parameters)),
      },
    }));

    // First AI call - may request tool use
    const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
      messages: [
        { role: "system", content: "You are a helpful assistant with access to tools." },
        ...this.state.messages,
        { role: "user", content: userMessage },
      ],
      tools: toolDescriptions,
    });

    // Check if AI wants to use a tool
    if (response.tool_calls) {
      for (const toolCall of response.tool_calls) {
        const tool = this.tools.get(toolCall.function.name);
        if (tool) {
          const params = JSON.parse(toolCall.function.arguments);
          const result = await tool.handler(params);

          // Send tool result back to AI
          const finalResponse = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
            messages: [
              ...this.state.messages,
              { role: "user", content: userMessage },
              { role: "assistant", tool_calls: response.tool_calls },
              { role: "tool", tool_call_id: toolCall.id, content: result },
            ],
          });

          connection.send(JSON.stringify({
            type: "response",
            content: finalResponse.response,
            toolUsed: toolCall.function.name,
          }));
        }
      }
    } else {
      connection.send(JSON.stringify({
        type: "response",
        content: response.response,
      }));
    }
  }
}
```

## RAG (Retrieval Augmented Generation)

Combine Vectorize with Agents for knowledge-grounded responses:

```typescript
interface Env {
  AI: Ai;
  VECTORIZE: VectorizeIndex;
}

export class RAGAgent extends Agent<Env, State> {
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      // 1. Generate embedding for query
      const embedding = await this.env.AI.run("@cf/baai/bge-base-en-v1.5", {
        text: data.content,
      });

      // 2. Search vector database
      const results = await this.env.VECTORIZE.query(embedding.data[0], {
        topK: 5,
        returnMetadata: true,
      });

      // 3. Build context from results
      const context = results.matches
        .map((m) => m.metadata?.text || "")
        .join("\n\n");

      // 4. Generate response with context
      const response = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
        messages: [
          {
            role: "system",
            content: `Answer based on this context:\n\n${context}\n\nIf the context doesn't contain relevant information, say so.`,
          },
          { role: "user", content: data.content },
        ],
      });

      // 5. Update state and respond
      this.setState({
        messages: [
          ...this.state.messages,
          { role: "user", content: data.content },
          { role: "assistant", content: response.response },
        ],
      });

      connection.send(JSON.stringify({
        type: "response",
        content: response.response,
        sources: results.matches.map((m) => m.metadata?.source),
      }));
    }
  }

  // Ingest documents into vector store
  async ingestDocument(doc: { id: string; text: string; source: string }) {
    const embedding = await this.env.AI.run("@cf/baai/bge-base-en-v1.5", {
      text: doc.text,
    });

    await this.env.VECTORIZE.upsert([{
      id: doc.id,
      values: embedding.data[0],
      metadata: { text: doc.text, source: doc.source },
    }]);
  }
}
```

## Multi-Agent Orchestration

Coordinate multiple specialized agents:

```typescript
interface Env {
  RESEARCHER: DurableObjectNamespace;
  WRITER: DurableObjectNamespace;
  REVIEWER: DurableObjectNamespace;
}

export class OrchestratorAgent extends Agent<Env, State> {
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "create_article") {
      connection.send(JSON.stringify({ type: "status", step: "researching" }));

      // Step 1: Research agent gathers information
      const researchResult = await this.callAgent(
        this.env.RESEARCHER,
        data.topic,
        { action: "research", topic: data.topic }
      );

      connection.send(JSON.stringify({ type: "status", step: "writing" }));

      // Step 2: Writer agent creates draft
      const draftResult = await this.callAgent(
        this.env.WRITER,
        data.topic,
        { action: "write", research: researchResult, topic: data.topic }
      );

      connection.send(JSON.stringify({ type: "status", step: "reviewing" }));

      // Step 3: Reviewer agent improves draft
      const finalResult = await this.callAgent(
        this.env.REVIEWER,
        data.topic,
        { action: "review", draft: draftResult }
      );

      connection.send(JSON.stringify({
        type: "complete",
        article: finalResult,
      }));
    }
  }

  private async callAgent(
    namespace: DurableObjectNamespace,
    id: string,
    payload: any
  ): Promise<string> {
    const agentId = namespace.idFromName(id);
    const agent = namespace.get(agentId);

    const response = await agent.fetch("http://agent/task", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    return response.text();
  }
}
```

## Human-in-the-Loop

Pause agent execution for human approval:

```typescript
interface State {
  pendingApprovals: Array<{
    id: string;
    action: string;
    data: any;
    requestedAt: string;
  }>;
}

export class ApprovalAgent extends Agent<Env, State> {
  initialState: State = { pendingApprovals: [] };

  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "request_action") {
      // Action requires approval
      if (this.requiresApproval(data.action)) {
        const approvalId = crypto.randomUUID();

        this.setState({
          pendingApprovals: [
            ...this.state.pendingApprovals,
            {
              id: approvalId,
              action: data.action,
              data: data.payload,
              requestedAt: new Date().toISOString(),
            },
          ],
        });

        connection.send(JSON.stringify({
          type: "approval_required",
          approvalId,
          action: data.action,
          description: this.describeAction(data.action, data.payload),
        }));

        return;
      }

      // Execute immediately if no approval needed
      await this.executeAction(connection, data.action, data.payload);
    }

    if (data.type === "approve") {
      const approval = this.state.pendingApprovals.find(
        (a) => a.id === data.approvalId
      );

      if (approval) {
        // Remove from pending
        this.setState({
          pendingApprovals: this.state.pendingApprovals.filter(
            (a) => a.id !== data.approvalId
          ),
        });

        // Execute the approved action
        await this.executeAction(connection, approval.action, approval.data);
      }
    }

    if (data.type === "reject") {
      this.setState({
        pendingApprovals: this.state.pendingApprovals.filter(
          (a) => a.id !== data.approvalId
        ),
      });

      connection.send(JSON.stringify({
        type: "action_rejected",
        approvalId: data.approvalId,
      }));
    }
  }

  private requiresApproval(action: string): boolean {
    const sensitiveActions = ["delete", "send_email", "make_payment", "publish"];
    return sensitiveActions.includes(action);
  }

  private describeAction(action: string, data: any): string {
    // Generate human-readable description
    return `${action}: ${JSON.stringify(data)}`;
  }

  private async executeAction(connection: Connection, action: string, data: any) {
    // Execute the action
    const result = await this.performAction(action, data);

    connection.send(JSON.stringify({
      type: "action_completed",
      action,
      result,
    }));
  }
}
```

## Streaming Responses

Stream AI responses in real-time:

```typescript
export class StreamingAgent extends Agent<Env, State> {
  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "chat") {
      // Start streaming response
      const stream = await this.env.AI.run("@cf/meta/llama-3-8b-instruct", {
        messages: [
          { role: "system", content: "You are a helpful assistant." },
          ...this.state.messages,
          { role: "user", content: data.content },
        ],
        stream: true,
      });

      let fullResponse = "";

      // Stream chunks to client
      for await (const chunk of stream) {
        if (chunk.response) {
          fullResponse += chunk.response;
          connection.send(JSON.stringify({
            type: "stream",
            content: chunk.response,
            done: false,
          }));
        }
      }

      // Update state with complete response
      this.setState({
        messages: [
          ...this.state.messages,
          { role: "user", content: data.content },
          { role: "assistant", content: fullResponse },
        ],
      });

      // Signal completion
      connection.send(JSON.stringify({
        type: "stream",
        content: "",
        done: true,
      }));
    }
  }
}
```

## Connecting to MCP Servers

Agents can connect to MCP servers as clients:

```typescript
export class MCPClientAgent extends Agent<Env, State> {
  async onStart() {
    // Connect to external MCP server
    await this.addMcpServer(
      "github",
      "https://github-mcp.example.com/sse",
      { headers: { Authorization: `Bearer ${this.env.GITHUB_TOKEN}` } }
    );

    await this.addMcpServer(
      "database",
      "https://db-mcp.example.com/sse"
    );
  }

  async onMessage(connection: Connection, message: string) {
    const data = JSON.parse(message);

    if (data.type === "use_tool") {
      // Call tool on connected MCP server
      const servers = await this.getMcpServers();
      const server = servers.find((s) => s.name === data.server);

      if (server) {
        const result = await server.callTool(data.tool, data.params);
        connection.send(JSON.stringify({ type: "tool_result", result }));
      }
    }
  }

  async onClose() {
    // Cleanup MCP connections
    await this.removeMcpServer("github");
    await this.removeMcpServer("database");
  }
}
```
