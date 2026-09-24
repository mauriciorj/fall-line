---
name: create-mountain-crawler
description: Create or update a ski mountain crawler under crawler/mountains using the repository's generator, snapshot, metadata, and Convex publishing conventions.
argument-hint: "[resort slug] [source URLs or requirements]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - write
  - edit
  - grep
  - glob
  - exec
---

Create or update a mountain crawler. Apply this workflow to requests involving `crawler/mountains/**`.

## 1. Inspect before editing

- Identify the target path: `crawler/mountains/<continent>/<country>/<region>/<resort-slug>/`.
- Read the nearest complete crawler in the same region. Prefer the same data shape and source type; use `antoine-mountain`, `brimacombe`, `blue-mountain`, or `mount-baldy` only after comparing them.
- Read the target directory, `crawler/requirements.txt`, and any local README.
- Check `git status` before changing generated JSON or existing user work.
- Verify the Python import root. Most Ontario crawlers use `Path(__file__).resolve().parent.parents[3]`; do not copy this blindly. Confirm the path that contains `convex_client.py`.

## 2. Required crawler contract

A standard mountain crawler contains:

```text
<resort-slug>/
├── main.py
├── snapshot_generator.py
├── static_infos.json
└── json_generators/
    ├── hours-of-operation.py
    ├── lift-rates.py
    ├── rentals.py
    ├── skiresort.py
    └── tracks-and-lifts-weather-status.py
```

Each generator writes a sibling JSON file. Each table payload must preserve:

```json
{
  "<data>": {},
  "resortId": "<resort-id>",
  "sourceUrl": "<verified-source-url>",
  "updatedAt": 0
}
```

Use the exact data key required by the table: `hours`, `rates`, `rentals`, or weather fields (`lifts`, `tracks`, and optional `terrainParks`). Unknown data may be empty, but keep metadata and schema valid. Do not fabricate prices, coordinates, ratings, trail names, or statuses.

## 3. Generator conventions

- Use `json`, `os` or `pathlib`, and `time` consistently with neighboring crawlers.
- Use `requests` with a timeout and `response.raise_for_status()` for HTTP sources.
- Use the existing `truststore.inject_into_ssl()` pattern only when the neighboring crawler needs it; dependencies already exist in `crawler/requirements.txt`.
- Use `BeautifulSoup` for HTML extraction. Normalize whitespace and labels before parsing.
- Keep source URLs explicit constants. Never hide, concatenate, encode, or invent external URLs.
- Every generator must guard execution with `if __name__ == "__main__":` because `snapshot_generator.py` runs every `*.py` in `json_generators` in sorted order.
- Preserve existing fallback behavior when a source lacks a section. If the requested state is unknown, return an empty object/list or an explicit closed/not-informed value according to the local reference crawler.

## 4. `snapshot_generator.py`

- Define `RESORT_ID`, `RESORT_NAME`, `SKI_RESORT_FIELDS`, `DIFFICULTY_FIELDS`, and `TABLE_COLUMNS`.
- Map SkiResort fields exactly:
  - `elevation` -> `elevation`
  - `height` -> `height`
  - `tracks-green-length` / `proportion` -> `tracksGreenLength` / `tracksGreenProportion`
  - same blue and black mappings
  - `tracks-total-length` -> `tracksTotalLength`
- Parse prices defensively. Return `None` when unavailable; only add optional price fields when a value exists.
- Build `tracksSummary` with exactly `black`, `blue`, `doubleBlack`, `freeStyle`, and `green`. Count terrain parks as `freeStyle` only when the local source model includes them. If a resort has known static trail counts but no live status data, encode that fallback explicitly as a named constant and test it.
- Copy `static_infos.json` before adding derived fields. Set `name` and `resortId` explicitly when the local convention does so.
- Run every generator through `subprocess.run(..., cwd=json_generators, check=True)`.
- Produce `snapshot_generator.json` and `snapshot_generator_report.json`.
- Keep the five tables: `resorts`, `resortHours`, `resortRates`, `resortRentals`, and `weatherAndStatus`.

## 5. `main.py`

- Generate and load the snapshot before publishing.
- Validate table names, object content, resort ID consistency, required metadata, and required resort fields.
- Convert dictionary hours to the Convex hours list shape:

```python
[
    {
        "name": "Hours of operation",
        "hours": [{"day": day, "time": time} for day, time in hours.items()],
    }
]
```

- Normalize weather `tracks` to Convex `trails`.
- Remove generator-only lift `area` fields before publishing when the local reference does so.
- Pass each table's original `updatedAt` to the corresponding `push_*` function.
- Never bypass publishing validation because a source is incomplete.

## 6. Static metadata

`static_infos.json` contains verified stable facts: identity, geography, contact, URLs, capabilities, publication state, and optional rating. Omit unavailable fields instead of guessing. Keep `resortId` aligned with every generator and the snapshot.

## 7. Verification checklist

Run from `crawler/` or the resort directory as appropriate:

```text
python -m py_compile <resort>/main.py <resort>/snapshot_generator.py <resort>/json_generators/*.py
python <resort>/snapshot_generator.py
```

Then verify:

- All five generated table payloads exist.
- Every table has matching `resortId`, `sourceUrl`, and numeric `updatedAt`.
- Snapshot resort ID matches resort table ID.
- Required SkiResort fields are populated before running `main.py`.
- Empty rates/rentals/status data remains schema-valid.
- `snapshot_generator_report.json` is reviewed; missing fields are expected only when source data is genuinely unavailable.
- Do not run `main.py` unless publishing side effects and credentials are intended.
