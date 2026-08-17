# Knowledge Sources

Add your real information as markdown files in this folder, then rebuild the index.

## Layout

```text
knowledge/sources/
  resume.md
  github/
    profile.md
  projects/
    your-project-name.md
```

## Frontmatter

Each document can declare source metadata at the top:

```yaml
---
source_id: unique-id
source_type: resume | project | github
title: Human-readable title
url: optional-link
---
```

If frontmatter is omitted, metadata is inferred from the file path.

## Rebuild the index

From the project root:

```bash
npm run knowledge:ingest
```

Or directly:

```bash
python -m knowledge.ingest
```

Run this again whenever you add or edit source documents.
