# Project Rules

- For changes under `crawler/mountains/**`, use `.devin/skills/create-mountain-crawler/SKILL.md`.
- Preserve the five-table crawler contract: `resorts`, `resortHours`, `resortRates`, `resortRentals`, and `weatherAndStatus`.
- Keep `resortId`, `sourceUrl`, and `updatedAt` in every generated table payload.
- Do not invent unavailable mountain data. Use explicit empty or closed/not-informed fallbacks.
- Compile generators and run the resort snapshot generator before completion. Review `snapshot_generator_report.json`.
- Do not run `main.py` unless Convex publishing side effects are intended.
