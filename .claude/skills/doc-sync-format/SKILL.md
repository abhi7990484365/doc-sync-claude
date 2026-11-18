---
name: doc-sync-format
description: Required structure of the generated docs/PROJECT_DOC.md and the "Not Found" rule. Use when designing, implementing, testing or reviewing the doc generator.
---

# PROJECT_DOC.md format

Generate exactly these level-2 sections, in this order:

1. `## Name`
2. `## Description`
3. `## Languages`
4. `## Dependencies`
5. `## Entry Points`
6. `## How to Run`
7. `## Last Commit`

The file starts with a single `# <Name>` title line, or `# Not Found` if the name is unknown.

## Not Found rule
- If a section's data is missing, unreadable or the repo is empty, the section body
  is exactly `Not Found` (no punctuation, no extra words).
- Never guess or invent content. Never omit a section.
- Lists (Languages, Dependencies, Entry Points) use `- item` lines; an empty list is `Not Found`.
- Last Commit format: `<short-sha> <date> <subject>`, otherwise `Not Found`.
- Never include secrets or environment variable values.
