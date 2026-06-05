# Recipe: Team / Staff Directory

Build a team directory using `@wix/data` — staff cards grouped by department with individual profile pages. Use for about us, our team, meet the staff, or any people directory.

> Read `CMS_FOUNDATIONS.md` (this folder — service module, query patterns, image resolution, elevation) for page-rendering patterns, and `../../cms/CMS_FOUNDATIONS.md` for REST-based seeding.

## Collection Schema

Create a collection in the Wix dashboard → CMS with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `name` | Text | Full name |
| `slug` | Text | URL-friendly identifier |
| `role` | Text | Job title or role |
| `department` | Text | Department or team (e.g., "Engineering", "Design") |
| `bio` | Rich Text | Bio or description (HTML) |
| `photo` | Image | Headshot (`wix:image://` — resolve with `media.getScaledToFillImageUrl()`) |
| `email` | Text | Contact email |
| `linkedIn` | URL | LinkedIn profile URL |
| `twitter` | URL | Twitter/X profile URL |
| `orderIndex` | Number | Manual sort order within department |

## Files to Create

| File | Purpose |
|------|---------|
| `src/lib/team.ts` | Service module — queries, department grouping |
| `src/pages/team/index.astro` | Department-sectioned directory |
| `src/pages/team/[slug].astro` | Individual member profile |
| `src/components/TeamMemberCard.astro` | Photo, name, role, social icons |

## Implementation

### 1. Team Service Module (`src/lib/team.ts`)

```typescript
import * as items from "@wix/wix-data-items-sdk";
import { auth } from "@wix/essentials";
import { media } from "@wix/sdk";

const COLLECTION_ID = "Team";

export interface TeamMember {
  _id: string;
  name: string;
  slug: string;
  role: string;
  department: string;
  bio?: string;
  photo?: string;
  email?: string;
  linkedIn?: string;
  twitter?: string;
  orderIndex: number;
}

function resolvePhoto(url: string | undefined): string | undefined {
  if (!url) return undefined;
  return media.getScaledToFillImageUrl(url, 400, 400, {});
}

function mapMember(item: Record<string, any>): TeamMember {
  return {
    _id: item._id,
    name: item.name ?? "",
    slug: item.slug ?? "",
    role: item.role ?? "",
    department: item.department ?? "",
    bio: item.bio,
    photo: resolvePhoto(item.photo),
    email: item.email,
    linkedIn: item.linkedIn,
    twitter: item.twitter,
    orderIndex: item.orderIndex ?? 0,
  };
}

export async function queryTeamMembers(): Promise<TeamMember[]> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .ascending("orderIndex")
    .limit(100)
    .find();

  return results.map(mapMember);
}

export async function getMemberBySlug(slug: string): Promise<TeamMember | null> {
  const elevatedQuery = auth.elevate(items.query);
  const { items: results } = await elevatedQuery(COLLECTION_ID)
    .eq("slug", slug)
    .limit(1)
    .find();

  const item = results[0];
  if (!item) return null;
  return mapMember(item);
}

export function groupByDepartment(members: TeamMember[]): Map<string, TeamMember[]> {
  return members.reduce((map, member) => {
    const dept = member.department || "Team";
    if (!map.has(dept)) map.set(dept, []);
    map.get(dept)!.push(member);
    return map;
  }, new Map<string, TeamMember[]>());
}
```

Key details:
- `resolvePhoto()` uses 400x400 for square headshot crops
- `groupByDepartment()` returns a `Map` preserving insertion order — departments appear in the order of their first member
- Update `COLLECTION_ID` to match the exact collection name from the Wix dashboard (no namespace prefix for native collections)

### 2. Team Member Card (`src/components/TeamMemberCard.astro`)

```astro
---
interface Props {
  member: {
    name: string;
    slug: string;
    role: string;
    photo?: string;
    email?: string;
    linkedIn?: string;
    twitter?: string;
  };
}

const { member } = Astro.props;
---

<a href={`/team/${member.slug}`}>
  <div>
    {member.photo ? (
      <img src={member.photo} alt={member.name} />
    ) : (
      <div>{member.name.charAt(0)}</div>
    )}
  </div>
  <h3>{member.name}</h3>
  <p>{member.role}</p>
  <div>
    {member.email && (
      <a href={`mailto:${member.email}`} onclick="event.stopPropagation()">Email</a>
    )}
    {member.linkedIn && (
      <a href={member.linkedIn} target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()">LinkedIn</a>
    )}
    {member.twitter && (
      <a href={member.twitter} target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation()">Twitter</a>
    )}
  </div>
</a>
```

> **Styling note:** TeamMemberCard styling is created by the design skill. See `COMPONENT_PATTERNS.md` → Team Member Card.

Key details:
- Inline SVG icons — no icon library dependency
- Fallback initial letter when no photo
- Social links use `onclick="event.stopPropagation()"` to prevent navigation to profile when clicking social icons

### 3. Team Directory Page (`src/pages/team/index.astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import TeamMemberCard from "../../components/TeamMemberCard.astro";
import { queryTeamMembers, groupByDepartment } from "../../lib/team";

const members = await queryTeamMembers();
const departments = groupByDepartment(members);
---

<Layout title="Our Team">
  <main>
    <div>
      <h1>Our Team</h1>

      {[...departments.entries()].map(([dept, deptMembers]) => (
        <section>
          <h2>{dept}</h2>
          <div>
            {deptMembers.map((member) => (
              <TeamMemberCard member={member} />
            ))}
          </div>
        </section>
      ))}

      {members.length === 0 && (
        <p>No team members found.</p>
      )}
    </div>
  </main>
</Layout>
```

### 4. Member Profile Page (`src/pages/team/[slug].astro`)

```astro
---
import Layout from "../../layouts/Layout.astro";
import { getMemberBySlug } from "../../lib/team";

const { slug } = Astro.params;
const member = await getMemberBySlug(slug!);
if (!member) return Astro.redirect("/404");
---

<Layout title={member.name}>
  <main>
    <div>
      <a href="/team">
        &larr; Back to team
      </a>

      <div>
        {member.photo && (
          <div>
            <img
              src={member.photo}
              alt={member.name}
            />
          </div>
        )}
        <div>
          <h1>{member.name}</h1>
          <p>{member.role}</p>
          {member.department && (
            <p>{member.department}</p>
          )}
          <div>
            {member.email && (
              <a href={`mailto:${member.email}`}>
                {member.email}
              </a>
            )}
            {member.linkedIn && (
              <a href={member.linkedIn} target="_blank" rel="noopener noreferrer">
                LinkedIn
              </a>
            )}
            {member.twitter && (
              <a href={member.twitter} target="_blank" rel="noopener noreferrer">
                Twitter
              </a>
            )}
          </div>
        </div>
      </div>

      {member.bio && (
        <article set:html={member.bio} />
      )}
    </div>
  </main>
</Layout>
```

## Seed with Images

> **Do not skip:** Team members without photos appear as initial-letter placeholders.
> Always ask the user if they want to generate headshot images before moving on.

After seeding team members via REST, generate headshot images following `../../shared/IMAGE_GENERATION.md` and `../../cms/CMS_FOUNDATIONS.md` → "Seeding with Images".

**Prompt template:**

```
Professional headshot portrait of [NAME], [ROLE] at [BUSINESS NAME]. [BRAND AESTHETIC]. Warm studio lighting, neutral background with [BRAND COLORS]. No text, no watermarks
```

**Patch field:** `photo`

Example: after generating and importing the image, patch the team member item:

```
REST: PATCH https://www.wixapis.com/wix-data/v2/items/{memberId}
body: {
  "dataCollectionId": "Team",
  "dataItem": {
    "data": {
      "photo": "<wixstatic-url>"
    }
  }
}
```

## Testing

1. Create a "Team" collection in the Wix dashboard → CMS with the schema above
2. Add 4+ members across 2+ departments, with photos and social links
3. Run `npx @wix/cli@latest dev`
4. `/team` — shows members grouped by department
5. Click a member — profile page with photo, bio, and social links