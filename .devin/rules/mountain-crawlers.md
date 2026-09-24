---
description: Conventions for ski mountain crawler work
trigger: glob
globs: "crawler/mountains/**/*.py"
---

For mountain crawler changes, use the `create-mountain-crawler` skill. Read a complete neighboring crawler before editing. Preserve the five-table snapshot contract, generator metadata (`resortId`, `sourceUrl`, `updatedAt`), explicit source URLs, and validation before publishing. Unknown source data must remain empty or omitted, never guessed. Run generator compilation and snapshot generation before completion.
