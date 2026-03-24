# Workflow DevKit — DurableAgent Patterns

## Basic DurableAgent

```ts
import { DurableAgent } from '@workflow/ai/agent'
import { openai } from '@ai-sdk/openai'
import { tool } from 'ai'
import { z } from 'zod'

const agent = new DurableAgent({
  model: openai('gpt-5.2'),
  system: 'You are a helpful research assistant.',
  tools: {
    searchWeb: tool({
      description: 'Search the web for information',
      inputSchema: z.object({ query: z.string() }),
      execute: async ({ query }) => {
        // Search implementation
        return { results: await webSearch(query) }
      },
    }),
    writeReport: tool({
      description: 'Write a report to a file',
      inputSchema: z.object({
        title: z.string(),
        content: z.string(),
      }),
      execute: async ({ title, content }) => {
        await writeFile(`reports/${title}.md`, content)
        return { written: true }
      },
    }),
  },
})
```

## Workflow Endpoint (Next.js)

```ts
// app/api/workflows/research/route.ts
'use workflow'

export async function POST(req: Request) {
  const { topic } = await req.json()

  const result = await agent.generateText({
    prompt: `Research "${topic}" thoroughly and produce a comprehensive report.`,
  })

  return Response.json({ report: result.text })
}
```

## Workflow with Human-in-the-Loop

```ts
'use workflow'

export async function processApplication(applicationId: string) {
  'use step'
  const app = await getApplication(applicationId)

  'use step'
  const aiReview = await agent.generateText({
    prompt: `Review this application: ${JSON.stringify(app)}`,
  })

  'use step'
  await notifyReviewer(aiReview.text)

  'use step'
  // Pauses here until human approves — could be hours or days
  const approval = await waitForEvent(`approval:${applicationId}`)

  'use step'
  if (approval.approved) {
    await acceptApplication(applicationId)
  } else {
    await rejectApplication(applicationId, approval.reason)
  }
}
```

## Workflow with Parallel Fan-Out

```ts
'use workflow'

export async function analyzeCompetitors(competitors: string[]) {
  'use step'
  const analyses = await Promise.all(
    competitors.map(async (competitor) => {
      'use step'
      return await agent.generateText({
        prompt: `Analyze ${competitor}'s product strategy.`,
      })
    })
  )

  'use step'
  const summary = await agent.generateText({
    prompt: `Synthesize these competitive analyses: ${analyses.map(a => a.text).join('\n\n')}`,
  })

  return summary.text
}
```
