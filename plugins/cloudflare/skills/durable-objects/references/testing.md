# Testing Durable Objects

Use `@cloudflare/vitest-pool-workers` to test DOs inside the Workers runtime.

## Setup

### Install Dependencies

```bash
npm i -D vitest@~3.2.0 @cloudflare/vitest-pool-workers
```

### vitest.config.ts

```typescript
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.toml" },
      },
    },
  },
});
```

### TypeScript Config (test/tsconfig.json)

```jsonc
{
  "extends": "../tsconfig.json",
  "compilerOptions": {
    "moduleResolution": "bundler",
    "types": ["@cloudflare/vitest-pool-workers"]
  },
  "include": ["./**/*.ts", "../src/worker-configuration.d.ts"]
}
```

### Environment Types (env.d.ts)

```typescript
declare module "cloudflare:test" {
  interface ProvidedEnv extends Env {}
}
```

## Unit Tests (Direct DO Access)

```typescript
import { env } from "cloudflare:test";
import { describe, it, expect } from "vitest";

describe("Counter DO", () => {
  it("should increment", async () => {
    const stub = env.COUNTER.getByName("test-counter");
    
    expect(await stub.increment()).toBe(1);
    expect(await stub.increment()).toBe(2);
    expect(await stub.getCount()).toBe(2);
  });

  it("isolates different instances", async () => {
    const stub1 = env.COUNTER.getByName("counter-1");
    const stub2 = env.COUNTER.getByName("counter-2");
    
    await stub1.increment();
    await stub1.increment();
    await stub2.increment();
    
    expect(await stub1.getCount()).toBe(2);
    expect(await stub2.getCount()).toBe(1);
  });
});
```

## Integration Tests (HTTP via SELF)

```typescript
import { SELF } from "cloudflare:test";
import { describe, it, expect } from "vitest";

describe("Worker HTTP", () => {
  it("should increment via POST", async () => {
    const res = await SELF.fetch("http://example.com?id=test", {
      method: "POST",
    });
    
    expect(res.status).toBe(200);
    const data = await res.json<{ count: number }>();
    expect(data.count).toBe(1);
  });

  it("should get count via GET", async () => {
    await SELF.fetch("http://example.com?id=get-test", { method: "POST" });
    await SELF.fetch("http://example.com?id=get-test", { method: "POST" });
    
    const res = await SELF.fetch("http://example.com?id=get-test");
    const data = await res.json<{ count: number }>();
    expect(data.count).toBe(2);
  });
});
```

## Direct Internal Access

Use `runInDurableObject()` to access instance internals and storage:

```typescript
import { env, runInDurableObject } from "cloudflare:test";
import { describe, it, expect } from "vitest";
import { Counter } from "../src";

describe("DO internals", () => {
  it("can verify storage directly", async () => {
    const stub = env.COUNTER.getByName("direct-test");
    await stub.increment();
    await stub.increment();

    await runInDurableObject(stub, async (instance: Counter, state) => {
      expect(instance).toBeInstanceOf(Counter);
      
      const result = state.storage.sql
        .exec<{ value: number }>(
          "SELECT value FROM counters WHERE name = ?",
          "default"
        )
        .one();
      expect(result.value).toBe(2);
    });
  });
});
```

## List DO IDs

```typescript
import { env, listDurableObjectIds } from "cloudflare:test";
import { describe, it, expect } from "vitest";

describe("DO listing", () => {
  it("can list all IDs in namespace", async () => {
    const id1 = env.COUNTER.idFromName("list-1");
    const id2 = env.COUNTER.idFromName("list-2");
    
    await env.COUNTER.get(id1).increment();
    await env.COUNTER.get(id2).increment();
    
    const ids = await listDurableObjectIds(env.COUNTER);
    expect(ids.length).toBe(2);
    expect(ids.some(id => id.equals(id1))).toBe(true);
    expect(ids.some(id => id.equals(id2))).toBe(true);
  });
});
```

## Testing Alarms

Use `runDurableObjectAlarm()` to trigger alarms immediately:

```typescript
import { env, runInDurableObject, runDurableObjectAlarm } from "cloudflare:test";
import { describe, it, expect } from "vitest";

describe("DO alarms", () => {
  it("can trigger alarms immediately", async () => {
    const stub = env.COUNTER.getByName("alarm-test");
    await stub.increment();
    await stub.increment();
    expect(await stub.getCount()).toBe(2);

    // Schedule alarm
    await runInDurableObject(stub, async (instance, state) => {
      await state.storage.setAlarm(Date.now() + 60_000);
    });

    // Execute immediately without waiting
    const ran = await runDurableObjectAlarm(stub);
    expect(ran).toBe(true);

    // Verify alarm handler ran (if it resets counter)
    expect(await stub.getCount()).toBe(0);

    // No alarm scheduled now
    const ranAgain = await runDurableObjectAlarm(stub);
    expect(ranAgain).toBe(false);
  });
});
```

Example alarm handler:
```typescript
async alarm(): Promise<void> {
  this.ctx.storage.sql.exec("DELETE FROM counters");
}
```

## Test Isolation

Each test gets isolated storage automatically. DOs from one test don't affect others:

```typescript
describe("Isolation", () => {
  it("first test creates DO", async () => {
    const stub = env.COUNTER.getByName("isolated");
    await stub.increment();
    expect(await stub.getCount()).toBe(1);
  });

  it("second test has fresh state", async () => {
    const ids = await listDurableObjectIds(env.COUNTER);
    expect(ids.length).toBe(0); // Previous test's DO is gone
    
    const stub = env.COUNTER.getByName("isolated");
    expect(await stub.getCount()).toBe(0); // Fresh instance
  });
});
```

## SQLite Storage Testing

```typescript
describe("SQLite", () => {
  it("can verify SQL storage", async () => {
    const stub = env.COUNTER.getByName("sqlite-test");
    await stub.increment("page-views");
    await stub.increment("page-views");
    await stub.increment("api-calls");

    await runInDurableObject(stub, async (instance, state) => {
      const rows = state.storage.sql
        .exec<{ name: string; value: number }>(
          "SELECT name, value FROM counters ORDER BY name"
        )
        .toArray();

      expect(rows).toEqual([
        { name: "api-calls", value: 1 },
        { name: "page-views", value: 2 },
      ]);

      expect(state.storage.sql.databaseSize).toBeGreaterThan(0);
    });
  });
});
```

## Running Tests

```bash
npx vitest        # Watch mode
npx vitest run    # Single run
```

package.json:
```json
{
  "scripts": {
    "test": "vitest"
  }
}
```
