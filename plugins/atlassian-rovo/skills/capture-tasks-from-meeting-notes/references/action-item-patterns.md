# Action Item Patterns Reference

Common patterns found in meeting notes and how to parse them.

---

## Pattern Categories

### Category 1: @Mentions (Highest Confidence)

**Format:** `@Name [action verb] [task]`

**Examples:**
```
@john to update documentation
@sarah will create the report  
@mike should review PR #123
@lisa needs to test the feature
```

**Parsing:**
- Assignee: Text immediately after @
- Task: Everything after action verb (to/will/should/needs to)
- Confidence: Very High (explicit assignment)

---

### Category 2: Name + Action Verb (High Confidence)

**Format:** `Name [action verb] [task]`

**Examples:**
```
John to update documentation
Sarah will create the report
Mike should review PR #123
Lisa needs to test the feature
```

**Parsing:**
- Assignee: First word(s) before action verb
- Task: Everything after action verb
- Confidence: High (clear structure)

**Action verbs to detect:**
- to, will, should, needs to, must, has to, is to, going to

---

### Category 3: Structured Action Format (High Confidence)

**Format:** `Action: Name - [task]` or `AI: Name - [task]`

**Examples:**
```
Action: John - update documentation
Action Item: Sarah - create the report
AI: Mike - review PR #123
Task: Lisa - test the feature
```

**Parsing:**
- Assignee: Between "Action:" and "-"
- Task: After "-"
- Confidence: High (structured format)

**Variants:**
- Action:
- Action Item:
- AI:
- Task:
- Assigned:

---

### Category 4: TODO Format (Medium Confidence)

**Format:** `TODO: [task] (Name)` or `TODO: [task] - Name`

**Examples:**
```
TODO: Update documentation (John)
TODO: Create report - Sarah
[ ] Review PR #123 (Mike)
- [ ] Test feature - Lisa
```

**Parsing:**
- Assignee: In parentheses or after "-"
- Task: Between TODO and assignee
- Confidence: Medium (format varies)

**Markers to detect:**
- TODO:
- [ ]
- - [ ]
- To-do:
- Action item:

---

### Category 5: Colon or Dash Format (Medium Confidence)

**Format:** `Name: [task]` or `Name - [task]`

**Examples:**
```
John: update documentation
Sarah - create the report
Mike: review PR #123
Lisa - test the feature
```

**Parsing:**
- Assignee: Before ":" or "-"
- Task: After ":" or "-"
- Confidence: Medium (could be other uses of colons/dashes)

**Detection:**
- Look for name-like word before ":" or "-"
- Followed by action verb or imperative
- Usually in bulleted lists

---

## Complex Patterns

### Multiple Assignees

**Format:** `Name1 and Name2 to [task]`

**Examples:**
```
John and Sarah to update documentation
Mike, Lisa to review PR
```

**Handling:**
- Create separate tasks for each person
- OR create one task, ask user who should be assigned
- Include both names in description

---

### Conditional Actions

**Format:** `Name to [task] if [condition]`

**Examples:**
```
John to update docs if approved
Sarah will create report pending review
```

**Handling:**
- Include condition in task description
- Note that it's conditional
- User can adjust later

---

### Time-Bound Actions

**Format:** `Name to [task] by [date]`

**Examples:**
```
John to update docs by EOD
Sarah will finish report by Friday
Mike to review before next meeting
```

**Handling:**
- Extract deadline and add to task description
- Could use due date field if available
- Include urgency in task

---

## Anti-Patterns (Not Action Items)

### Discussion Notes

**Not an action item:**
```
John mentioned the documentation needs updating
Sarah suggested we create a report
Mike talked about reviewing the code
```

**Why:** These are discussions, not assignments

---

### General Statements

**Not an action item:**
```
Documentation needs to be updated
Someone should create a report
The code requires review
```

**Why:** No specific assignee

---

### Past Actions

**Not an action item:**
```
John updated the documentation
Sarah created the report
Mike reviewed the code
```

**Why:** Already completed (past tense)

---

## Context Extraction

### Meeting Metadata

**Look for:**
```
# [Meeting Title] - [Date]
Meeting: [Title]
Date: [Date]
Subject: [Title]
```

**Extract:**
- Meeting title
- Date
- Attendees (if listed)

---

### Related Information

**Look for:**
```
Related to: [project/epic/initiative]
Context: [background info]
Decision: [relevant decision]
```

**Include in task:**
- Links to related work
- Background context
- Relevant decisions

---

## Name Extraction Tips

### Full Names

**Preferred:**
```
@Sarah Johnson to create report
Sarah Johnson will create report
```

**Extract:** "Sarah Johnson"

---

### First Name Only

**Common:**
```
@Sarah to create report
Sarah will create report
```

**Extract:** "Sarah" (will need to lookup)

---

### Nicknames or Short Forms

**Handle carefully:**
```
@SJ to create report
Sara (no h) will create report
```

**Strategy:** Ask user or try multiple lookups

---

## Priority Indicators

### Urgent/High Priority

**Detect:**
```
URGENT: John to update docs
HIGH PRIORITY: Sarah to create report
ASAP: Mike to review code
```

**Handling:**
- Note priority in task description
- Could set priority field
- Highlight in presentation

---

### Low Priority

**Detect:**
```
If time: John to update docs
Nice to have: Sarah create report
Eventually: Mike review code
```

**Handling:**
- Note as lower priority
- Could defer creation
- User can decide

---

## Confidence Scoring

When parsing, assign confidence:

**High Confidence (90%+):**
- @Mentions with clear action
- "Name to do X" format
- "Action: Name - X" format

**Medium Confidence (60-90%):**
- Name: task format
- TODO with name
- Name without action verb but clear task

**Low Confidence (<60%):**
- Ambiguous wording
- No clear assignee
- Could be discussion not action

**Handling:**
- Present all to user
- Flag low-confidence items
- Let user confirm or skip

---

## Special Cases

### Group Actions

```
Everyone to review the document
Team to provide feedback
```

**Handling:**
- Ask user who specifically
- OR create one task unassigned
- Note it's for the whole team

---

### Optional Actions

```
Sarah could create a report if needed
Mike might review the code
```

**Handling:**
- Flag as optional
- Ask user if should create
- Include "optional" in description

---

### Delegated Actions

```
John will ask Sarah to create the report
```

**Handling:**
- Assign to Sarah (the actual doer)
- Note John is requestor
- Include context

---

## Testing Patterns

Use these to validate pattern matching:

```
✅ @john to update tests
✅ Sarah will write docs
✅ Mike: review code
✅ TODO: Deploy (Lisa)
✅ Action: John - fix bug

⚠️ Maybe John can help?
⚠️ Documentation needs work
⚠️ We should test this

❌ John mentioned testing
❌ Tests were updated
❌ Someone needs to deploy
```

---

## Regular Expression Examples

**@Mention pattern:**
```regex
@(\w+)\s+(to|will|should)\s+(.+)
```

**Name + action verb:**
```regex
([A-Z][\w\s]+?)\s+(to|will|should)\s+(.+)
```

**Action format:**
```regex
Action:\s*([A-Z][\w\s]+?)\s*-\s*(.+)
```

**TODO format:**
```regex
TODO:\s*(.+)\s*\((\w+)\)
```

**Note:** These patterns use `[A-Z][\w\s]+?` to match names flexibly:
- Starts with a capital letter
- Matches one or more word characters or spaces
- Non-greedy (`+?`) to stop at action verbs
- Handles single names ("Sarah"), two-part names ("Sarah Johnson"), and longer names ("Mary Jane Smith")
