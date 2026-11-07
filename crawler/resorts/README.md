# Resort basics

Publishes the **basic resort info** (identity, contact, geography, run lengths) to Convex.
Only the `resorts` table is touched. Hours, rates, rentals and weather are not.

Data comes from two files per resort. `static_infos.json` wins over `skiresort.json`.

| File | Source |
|---|---|
| `static_infos.json` | Verified manual facts (address, contact, `published`, `rating`, `has*` flags...) |
| `json_generators/skiresort.json` | Scraped from skiresort.com (elevation, height, run lengths and proportions) |

## Layout

```text
crawler/resorts/
├── basics.py                  # runner: runs every resort basics.py (this file)
├── README.md
└── <country>/<region>/<resort-slug>/
    ├── basics.py              # per-resort: scrape -> basics.json -> push to Convex
    ├── static_infos.json
    └── json_generators/
        ├── skiresort.py       # scrapes skiresort.com
        └── skiresort.json     # generated
```

`basics.json` is generated next to each resort `basics.py`, with the same shape as `snapshot_generator.json` but with the `resorts` table only:

```json
{ "resortId": "<id>", "tables": [{ "table": "resorts", "content": { } }] }
```

## Setup

From `crawler/`:

```text
python -m venv venv
venv\Scripts\activate            # Windows (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Convex access:
- `crawler/.env.local` (or the repo root `.env.local`) must define `CONVEX_DEPLOYMENT` or `CONVEX_DEPLOY_KEY`.
- The Convex CLI must be installed (`pnpm install` at the repo root).
- `convex_client.py` already runs the CLI with `node --use-system-ca`, so the corporate TLS proxy needs no extra setting.

## Run everything or a subset

Run from `crawler/resorts/`. The country and region names are the folder names (case-insensitive).

```text
python basics.py                          # ALL resorts in every country
python basics.py canada                   # all resorts in a country
python basics.py canada alberta           # all resorts in one region
python basics.py canada alberta --dry-run # list what would run, no scraping, no push
```

- Empty (0-byte) `basics.py` files are skipped and reported, not counted as successes. Currently skipped on purpose: `british-columbia/big-white` (its `skiresort.py` is a stub with no scraping) and `british-columbia/sun-peaks` (duplicate of `sun-peaks-resort`).
- A region without a country is rejected.
- An unknown country or region prints the available names.
- Each resort runs in its own process. One failure does not stop the others.
- Failures are listed at the end, appended to `crawler/crawler-errors.log`, and the exit code is `1`.
- **Every run pushes to Convex.** Use `--dry-run` first to check the scope.

## Run one resort

```text
cd crawler/resorts/canada/alberta/<resort-slug>
python basics.py
```

Steps, in order:
1. Runs `json_generators/skiresort.py`, which writes `skiresort.json`.
2. Builds `basics.json`: `skiresort.json` fields first, then `static_infos.json` on top (static wins), plus `name`.
3. Validates it: single `resorts` table, `resortId` matches, `name` and all `skiresort` fields present.
4. Pushes the resort with `push_ski_resorts` (`resorts:saveMany`), which upserts by `resortId` and sets `updatedAt`.

To check without publishing, import the module instead of running it:

```text
python -c "import basics; basics.run_skiresort_generator(); b = basics.build_basics(); basics.write_basics(b); basics.validate_basics(b)"
```

This regenerates `skiresort.json` and `basics.json` and runs validation, but does not push.

## Fields mapping

| `skiresort.json` | Convex field |
|---|---|
| `elevation`, `height` | `elevation`, `height` |
| `tracks-green-length` / `-proportion` | `tracksGreenLength` / `tracksGreenProportion` |
| `tracks-blue-length` / `-proportion` | `tracksBlueLength` / `tracksBlueProportion` |
| `tracks-black-length` / `-proportion` | `tracksBlackLength` / `tracksBlackProportion` |
| `tracks-total-length` | `tracksTotalLength` |

Other fields come from `static_infos.json`. `coordinates.lat` and `coordinates.lng` are converted to numbers; if either is empty, `coordinates` is left out.

## Adding a resort

1. Create `<country>/<region>/<resort-slug>/` with `static_infos.json` and `json_generators/skiresort.py`.
   - `resortId` in `static_infos.json` must equal the folder name.
   - `skiresort.py` must use the skiresort.com slug of the resort.
2. Copy `basics.py` from a neighbouring resort. Change only `RESORT_ID` and `RESORT_NAME`.
3. Run `python basics.py --dry-run`, then run the resort alone and check `basics.json`.

## Check before pushing

Static values overwrite what is in Convex.

- `name`: `static_infos.json` has no `name`, so `RESORT_NAME` in each `basics.py` is used.
- Empty values: the British Columbia, Manitoba and `banff-sunshine` `basics.py` skip empty/`None` static values, so they never blank Convex. The other Alberta `basics.py` files do not: an empty `""` (`phone`, `email`, `ticketUrl`...) there blanks the stored value. Fill it in or delete the key.
- `published`: missing means the field is not sent, so a new resort stays hidden on the site. `false` unpublishes it.
- `googleMapsUrl` and `website` must be real URLs. Some were derived from the email address.
- `resortId` must match the folder name, because `basics.py` forces it.

## Troubleshooting

| Error | Cause |
|---|---|
| `Could not find ... slope information` | The skiresort.com page layout changed or the slug is wrong. Open the URLs in `skiresort.py`. |
| `Missing ski resort information: [...]` | A required field is empty in the scraped or static data. |
| `Convex is not configured` | Missing `CONVEX_DEPLOYMENT` or `CONVEX_DEPLOY_KEY` in `.env.local`. |
| `Convex CLI not found` | Run `pnpm install` at the repo root. |
