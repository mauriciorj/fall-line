# Repository scripts

Scripts directory:

```text
scripts/
└── update-locations.py
```

`update-locations.py` synchronizes the Convex `locations` table from location data derived from the existing `resorts` table.

## `update-locations.py`

Path:

```text
scripts/update-locations.py
```

### Execution

Run from the repository root:

```powershell
python scripts/update-locations.py
```

Run from the scripts directory:

```powershell
cd scripts
python update-locations.py
```

### Workflow

1. Imports the shared Convex client from `crawler/convex_client.py`.
2. Calls the Convex query `resorts:listLocations` with no arguments.
3. Normalizes every returned location.
4. Removes invalid records without `continent` or `country`.
5. Replaces missing or blank `region` with `Unknown`.
6. Deduplicates locations case-insensitively by `(continent, country, region)`.
7. Sorts locations by continent, country, and region using case-insensitive ordering.
8. Calls the Convex internal mutation `locations:sync`.
9. Prints the number of resort records loaded and unique locations synchronized.

### Input

The query receives no arguments:

```text
resorts:listLocations()
```

The query reads every resort and returns these fields:

```json
{
  "continent": "North America",
  "country": "Canada",
  "region": "Ontario"
}
```

### Normalization rules

For each record:

- `continent` is trimmed.
- `country` is trimmed.
- `region` is trimmed.
- Records with an empty `continent` or `country` are discarded.
- Empty `region` becomes `Unknown`.
- Duplicate keys are collapsed using case-insensitive comparison.
- The first casing encountered for each unique key is retained.
- Final output is sorted case-insensitively by `continent`, `country`, then `region`.

Example duplicate key:

```text
("North America", "Canada", "Ontario")
("north america", "canada", "ontario")
```

Both resolve to one stored location.

### Output

The script does not write a local file. It sends this payload to Convex:

```json
{
  "locations": [
    {
      "continent": "North America",
      "country": "Canada",
      "region": "Ontario"
    }
  ]
}
```

Console output:

```text
Loaded <number> resort records
Synchronized <number> unique locations
```

## Convex operations

### Query: `resorts:listLocations`

Implemented in:

```text
convex/resorts.ts
```

The query collects all resort records and returns only `continent`, `country`, and `region`.

### Mutation: `locations:sync`

Implemented in:

```text
convex/locations.ts
```

The mutation:

1. Deletes every existing document in the `locations` table.
2. Inserts the normalized locations from the script.
3. Returns the number of inserted locations.

This is a full replacement operation, not an incremental upsert. Run only when a complete resort dataset is available. The mutation can temporarily leave the table empty if the operation fails after deletion.

The `locations` table schema is:

| Column | Type | Required |
| --- | --- | --- |
| `continent` | string | yes |
| `country` | string | yes |
| `region` | string | yes |

The table has a `by_location` index on `continent`, `country`, and `region`.

## Configuration

`crawler/convex_client.py` loads environment files from:

- project `.env`
- `crawler/.env`
- project `.env.local`
- `crawler/.env.local`

Required Convex configuration:

- `CONVEX_DEPLOYMENT`, or
- `CONVEX_DEPLOY_KEY`, or
- `CONVEX_ADMIN_KEY`

The Convex CLI must exist at:

```text
node_modules/convex/bin/main.js
```

The client invokes the CLI with Node and runs the Convex function through the configured deployment.

Do not place credentials in command arguments or source files.

## Python dependencies

The script requires `python-dotenv`, provided by the crawler requirements file:

```powershell
python -m pip install -r crawler/requirements.txt
```

The project must also have Node dependencies installed:

```powershell
pnpm install
```

## Failure behavior

The script raises when:

- Convex configuration is missing.
- The Convex CLI is unavailable.
- The Convex query fails.
- The Convex mutation fails.
- Convex returns invalid JSON.

No local recovery file is generated.

## Validation without writing locations

There is no dry-run flag. To test normalization without calling Convex, import `normalize_locations` from a Python test or temporary local harness and pass fixture records.

Do not call `update-locations.py` in production-like environments unless a full replacement of the current `locations` table is intended.
