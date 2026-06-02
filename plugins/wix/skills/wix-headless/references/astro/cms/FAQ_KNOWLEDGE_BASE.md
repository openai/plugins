# Recipe: FAQ / Knowledge Base

Build a FAQ page using `@wix/data` — Q&A pairs organized by category with accordion UI and client-side search. Use for frequently asked questions, help centers, or knowledge bases.

> Read `CMS_FOUNDATIONS.md` (this folder — service module, query patterns, image resolution, elevation) for page-rendering patterns, and `../../cms/CMS_FOUNDATIONS.md` for REST-based seeding.

## Collection Schema

Create a collection in the Wix dashboard → CMS with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `question` | Text | The question |
| `slug` | Text | URL-friendly identifier (for anchor links) |
| `answer` | Rich Text | The answer (HTML) |
| `category` | Text | FAQ category (e.g., "Shipping", "Returns") |
| `orderIndex` | Number | Manual sort order within category |
| `published` | Boolean | Publish status |

## Files to Create

| File | Purpose |
|------|---------|
| `src/lib/faq.ts` | Service module — queries, category grouping |
| `src/pages/faq/index.astro` | Single FAQ page with category sections |
| `src/components/FaqSection.tsx` | React island — accordion + search combined |

> FAQ is a single-page pattern — no detail pages needed.

## Implementation

### 1. FAQ Service Module (`src/lib/faq.ts`)

```typescript
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";

const COLLECTION_ID = "FAQ";

export interface FaqItem {
  _id: string;
  question: string;
  slug: string;
  answer: string;
  category: string;
  orderIndex: number;
}

function mapFaqItem(item: Record<string, any>): FaqItem {
  return {
    _id: item._id,
    question: item.question ?? "",
    slug: item.slug ?? "",
    answer: item.answer ?? "",
    category: item.category ?? "General",
    orderIndex: item.orderIndex ?? 0,
  };
}

export async function queryFaqItems(): Promise<FaqItem[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("published", true)
    .ascending("orderIndex")
    .limit(200)
    .find();

  return results.map(mapFaqItem);
}

export function groupByCategory(faqItems: FaqItem[]): Map<string, FaqItem[]> {
  return faqItems.reduce((map, item) => {
    const cat = item.category || "General";
    if (!map.has(cat)) map.set(cat, []);
    map.get(cat)!.push(item);
    return map;
  }, new Map<string, FaqItem[]>());
}
```

Key details:
- No image resolution needed — FAQ items are text-only
- `published` filter ensures draft items don't appear
- Higher limit (200) since FAQ items are lightweight
- Update `COLLECTION_ID` to match the exact collection name from the Wix dashboard (no namespace prefix for native collections)

### 2. FAQ Section React Island (`src/components/FaqSection.tsx`)

```tsx
import { useState } from "react";

interface FaqItem {
  _id: string;
  question: string;
  slug: string;
  answer: string;
  category: string;
}

interface Props {
  categories: Array<{ name: string; items: FaqItem[] }>;
}

export default function FaqSection({ categories }: Props) {
  const [search, setSearch] = useState("");
  const query = search.toLowerCase().trim();

  const filtered = query
    ? categories
        .map((cat) => ({
          ...cat,
          items: cat.items.filter(
            (item) =>
              item.question.toLowerCase().includes(query) ||
              item.answer.toLowerCase().includes(query)
          ),
        }))
        .filter((cat) => cat.items.length > 0)
    : categories;

  return (
    <div>
      <div>
        <input
          type="text"
          placeholder="Search questions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="faq-search"
        />
      </div>

      {filtered.length === 0 && (
        <p>No matching questions found.</p>
      )}

      {filtered.map((cat) => (
        <section key={cat.name} className="faq-section" id={cat.name.toLowerCase().replace(/\s+/g, "-")}>
          <h2 className="faq-category">{cat.name}</h2>
          <div>
            {cat.items.map((item) => (
              <details key={item._id} className="faq-item" id={item.slug}>
                <summary className="faq-question">
                  <span>{item.question}</span>
                  <svg
                    className="faq-toggle"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </summary>
                <div
                  className="faq-answer"
                  dangerouslySetInnerHTML={{ __html: item.answer }}
                />
              </details>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
```

> **Styling note:** Uses `.faq-search`, `.faq-section`, `.faq-category`, `.faq-item`, `.faq-question`, `.faq-toggle`, `.faq-answer` from the designed component's `<style is:global>` block. See `COMPONENT_PATTERNS.md` → FAQ Accordion.

Key details:
- `<details>/<summary>` for native accordion behavior — no JavaScript needed for open/close
- CSS transition on the chevron via the `.faq-toggle` class
- Client-side search filters across both question and answer text
- `dangerouslySetInnerHTML` for rich text answers (content is from the CMS, not user input)
- Anchor `id` on each category section and question for direct linking

### 3. FAQ Page (`src/pages/faq/index.astro`)

**Layout width:** Center the page column with `container-reading` (from designer `global.css`) or `max-w-6xl mx-auto px-lg` when `--container-6xl` exists in `@theme`. **Do not** use `max-w-3xl` unless `--container-3xl` is declared in `@theme` — with only a spacing scale, Tailwind maps `max-w-3xl` to ~5rem and the FAQ collapses to one word per line. See `references/shared/STYLING.md` § "Prose / reading width".

```astro
---
import Layout from "../../layouts/Layout.astro";
import FaqSection from "../../components/FaqSection";
import { queryFaqItems, groupByCategory } from "../../lib/faq";

const faqItems = await queryFaqItems();
const grouped = groupByCategory(faqItems);
const categories = [...grouped.entries()].map(([name, items]) => ({ name, items }));
---

<Layout title="FAQ">
  <main>
    <div class="container-reading px-lg">
      <h1>Frequently Asked Questions</h1>
      <p>Find answers to common questions below, or use the search to find what you need.</p>

      {categories.length > 1 && (
        <nav>
          {categories.map((cat) => (
            <a
              href={`#${cat.name.toLowerCase().replace(/\s+/g, "-")}`}
            >{cat.name}</a>
          ))}
        </nav>
      )}

      <FaqSection client:only="react" categories={categories} />
    </div>
  </main>
</Layout>
```

Key details:
- Category jump links in the nav work because `FaqSection` renders matching `id` attributes
- `client:only="react"` — required for search state
- Data is fetched server-side and passed as props to the React island

## Testing

1. Create a "FAQ" collection in the Wix dashboard → CMS with the schema above
2. Add 6+ FAQ items across 2+ categories, all with `published: true`
3. Run `npx @wix/cli@latest dev`
4. `/faq` — shows all questions grouped by category
5. Click a question — accordion opens with the answer
6. Type in search — filters questions in real-time
7. Click a category jump link — scrolls to that section