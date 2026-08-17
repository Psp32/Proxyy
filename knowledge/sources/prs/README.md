# Pull Requests & Open Source Contributions

Add your 12 pull request markdown files in this folder (`knowledge/sources/prs/`).

You can create one `.md` file per PR (e.g. `pr-01.md`, `pr-02.md`, ... `pr-12.md`), or name them by project (e.g. `cal-com-pr.md`, `nextjs-pr.md`).

## Recommended Format for Each PR File

```markdown
---
source_id: pr-01-feature-name
source_type: github
title: Title of Contribution or PR
url: https://github.com/owner/repo/pull/123
---

# Overview

Brief description of what this pull request does, the problem it solved, and the context.

# Repository Information

* Repository: owner/repo
* PR Link: https://github.com/owner/repo/pull/123
* Status: Merged
* Technologies Used: TypeScript, React, Python, etc.

# Key Changes & Implementation

* Implemented feature X using approach Y.
* Resolved bug where Z occurred.
* Added tests covering the new functionality.

# Impact

Summary of the contribution's impact on the project.
```

Whenever you add or update files in this folder, run:
```bash
python -m agent.knowledge.ingest
```
