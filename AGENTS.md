# Project Rules

- For changes under `crawler/mountains/**`, use `.devin/skills/create-mountain-crawler/SKILL.md`.
- Preserve the five-table crawler contract: `resorts`, `resortHours`, `resortRates`, `resortRentals`, and `weatherAndStatus`.
- Keep `resortId`, `sourceUrl`, and `updatedAt` in every generated table payload.
- Do not invent unavailable mountain data. Use explicit empty or closed/not-informed fallbacks.
- Compile generators and run the resort snapshot generator before completion. Review `snapshot_generator_report.json`.
- Do not run `main.py` unless Convex publishing side effects are intended.
- SEO env: set `NEXT_PUBLIC_SITE_URL` (production origin, used for `metadataBase`/canonical/OG URLs; falls back to `VERCEL_PROJECT_PRODUCTION_URL`, then `http://localhost:3000`) and optionally `GOOGLE_SITE_VERIFICATION` (Search Console token).
- `next build` calls the Convex deployment (`NEXT_PUBLIC_CONVEX_URL`) for `generateStaticParams`; pages use `dynamic = "force-static"` + `revalidate` because `convex/nextjs` forces `cache: "no-store"`.
