# Super crawler (hybrid discovery)

Two-step workflow to onboard any ski resort website.

1. **Discovery (generic, run once per site)**: `super_crawler.py` crawls the whole site and writes a
   discovery report plus a draft `static_infos.json`.
2. **Per-resort generators (deterministic)**: build `hours-of-operation.py`, `lift-rates.py`,
   `rentals.py` and `tracks-and-lifts-weather-status.py` under `crawler/resorts/<country>/<region>/<resortId>/`
   using the `create-mountain-crawler` skill and the page map from `discovery.json`.

Daily runs only use the step 2 generators; discovery is not needed after onboarding.

## How to run

From `crawler/`:

```text
python super-crawler/super_crawler.py https://www.example-resort.com/
python super-crawler/super_crawler.py https://www.example-resort.com/ --max-pages 300 --render
python super-crawler/super_crawler.py https://www.example-resort.com/ --resort-id example-resort --region Ontario
```

| Option | Default | Description |
|---|---|---|
| `--max-pages` | 150 | Maximum HTML pages fetched. Relevant pages (tickets, rentals, trails, contact...) are fetched first. |
| `--max-depth` | 4 | Maximum link depth from the start URL. |
| `--delay` | 1.0 | Seconds between requests. |
| `--render` | off | Re-fetch JavaScript-only pages with headless Chrome (Selenium). |
| `--resort-id`, `--name`, `--country`, `--region`, `--continent` | derived | Overrides for the draft `static_infos.json`. |
| `--output-dir` | `output/<resortId>` | Output folder, relative to `super-crawler/` (a leading `/` also means `super-crawler/`). Use a drive path (`C:/...`) for anywhere else. |

Crawl rules: same host only, honors `robots.txt`, seeds from `sitemap.xml`, skips assets, blog/news/account
pages and other language prefixes (`/fr/`, `/en/`...) different from the start URL. PDFs are listed, not parsed.

## Outputs

- `discovery.json`
  - `facts`: ranked candidates with source URLs for `names`, `emails`, `phones`, `addresses`, plus
    `coordinates` and `openingHours` from schema.org JSON-LD.
  - `activities`: `hasIceSkate`, `hasCrossCountry`, `hasLessons`, `hasSnowshoeing`, `hasSpa`, `hasTubing`,
    `hasZipline` with `value` (`true`/`false`/`null`), `confidence` and evidence snippets.
    `false` is only set when the crawl completed and no page mentions the activity.
  - `pageMap`: top candidate pages for `contact`, `hours`, `rates`, `rentals`, `trails`, `lessons`, with price/
    schedule snippets, tables, trail/difficulty markers, iframes, API endpoints and `needsJs`.
  - `documents`: PDF links (rate cards, trail maps) with categories.
  - `thirdParty`: iframe domains and API endpoints (trail status/ticket widgets).
  - `needsReview`: what must be checked manually before building generators.
- `static_infos.draft.json`: draft with only the values found (unknown fields omitted, `published: false`).
  Review it, then copy it to the resort folder as `static_infos.json`.

## Step 2: generators

Ask the agent to apply the `create-mountain-crawler` skill with the discovery file, e.g.:

```text
Create the crawler for <resortId> in crawler/resorts/canada/<region>/<resortId> using
crawler/super-crawler/output/<resortId>/discovery.json
```

The generators must parse the HTML of the URLs listed in `pageMap` (Selenium when `needsJs` is true).
Never copy discovery snippets as static data.
