"""Enrich a skiresortinfo resorts list with Google Maps data.

Reads a resorts list JSON (array of objects), queries the Google Places API
(new) Text Search once per resort, and writes a new JSON file adding:

  - googleMapsUrl       canonical Google Maps link (googleMapsURI)
  - googlePlaceId       Google place resource name
  - googleAddress       formatted address from Google
  - rating              Google rating (null if not enough reviews)
  - userRatingCount     number of ratings
  - coordinates         {lat, lng} from Google

Resorts already enriched in the output file are skipped on re-run (--force
re-fetches everything). Missing data is set to null - never invented.

Usage:
  set GOOGLE_PLACES_API_KEY=...          (or pass --api-key)
  python enrich_with_google.py <input.json> [-o <output.json>] [--dry-run] [--force]

Example:
  python enrich_with_google.py canada/alberta/ski-resorts-list.json
  -> canada/alberta/ski-resorts-list-with-google.json
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.rating,"
    "places.userRatingCount,places.location,places.googleMapsURI"
)
DEFAULT_DELAY = 0.5  # seconds between API calls


def build_query(resort):
    name = resort.get("name", "")
    name = re.sub(r"\(temporarily closed\)", "", name, flags=re.IGNORECASE).strip()
    parts = [name]
    address = resort.get("address", "")
    if address:
        parts.append(address)
    parts.append(resort.get("region", ""))
    parts.append(resort.get("country", ""))
    return ", ".join(p for p in parts if p)


def search_place(query, api_key):
    response = requests.post(
        PLACES_URL,
        headers={
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
            "Content-Type": "application/json",
        },
        json={"textQuery": query, "languageCode": "en"},
        timeout=30,
    )
    response.raise_for_status()
    places = response.json().get("places", [])
    return places[0] if places else None


def merge_place(resort, place):
    out = dict(resort)
    out["googleMapsUrl"] = place.get("googleMapsURI")
    out["googlePlaceId"] = place.get("id")
    out["googleAddress"] = place.get("formattedAddress")
    out["rating"] = place.get("rating")
    out["userRatingCount"] = place.get("userRatingCount")
    location = place.get("location") or {}
    if "latitude" in location and "longitude" in location:
        out["coordinates"] = {
            "lat": location["latitude"],
            "lng": location["longitude"],
        }
    else:
        out["coordinates"] = None
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="resorts list JSON file")
    parser.add_argument("-o", "--output", help="output JSON (default: <input>-with-google.json)")
    parser.add_argument("--api-key", help="Google Places API key (default: GOOGLE_PLACES_API_KEY env)")
    parser.add_argument("--dry-run", action="store_true", help="print queries only, no API calls")
    parser.add_argument("--force", action="store_true", help="re-fetch resorts already enriched")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help=f"seconds between calls (default {DEFAULT_DELAY})")
    args = parser.parse_args()

    input_path = Path(args.input)
    with open(input_path, encoding="utf-8") as f:
        resorts = json.load(f)

    output_path = Path(args.output) if args.output else input_path.with_name(
        input_path.stem + "-with-google.json"
    )
    existing = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            for r in json.load(f):
                existing[r.get("resortId")] = r

    api_key = args.api_key or os.environ.get("GOOGLE_PLACES_API_KEY")
    if not args.dry_run and not api_key:
        sys.exit("Error: no API key. Set GOOGLE_PLACES_API_KEY or pass --api-key.")

    enriched, failures, skipped = [], [], 0
    for i, resort in enumerate(resorts, 1):
        resort_id = resort.get("resortId")
        if not args.force and resort_id in existing and existing[resort_id].get("googleMapsUrl"):
            enriched.append(existing[resort_id])
            skipped += 1
            continue

        query = build_query(resort)
        if args.dry_run:
            print(f"[{i}/{len(resorts)}] {resort_id}: {query}")
            enriched.append(resort)
            continue

        try:
            place = search_place(query, api_key)
        except requests.RequestException as e:
            print(f"[{i}/{len(resorts)}] {resort_id}: request failed: {e}", file=sys.stderr)
            failures.append(resort_id)
            enriched.append(resort)
            time.sleep(args.delay)
            continue

        if place is None:
            print(f"[{i}/{len(resorts)}] {resort_id}: no Google place found for: {query}", file=sys.stderr)
            failures.append(resort_id)
            enriched.append(resort)
        else:
            print(f"[{i}/{len(resorts)}] {resort_id}: ok ({place.get('rating')} / {place.get('userRatingCount')} ratings)")
            enriched.append(merge_place(resort, place))
        time.sleep(args.delay)

    if not args.dry_run:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f, ensure_ascii=False, indent=2)
            f.write("\n")

    if args.dry_run:
        print(f"Dry run complete: {len(resorts)} queries would be sent ({len(resorts)} Places API calls).")
        print(f"Output would be written to {output_path}")
    else:
        print(f"\nWrote {len(enriched)} resorts to {output_path}")
        if skipped:
            print(f"Skipped {skipped} already-enriched resorts (use --force to re-fetch).")
        if failures:
            print(f"No Google match for {len(failures)} resorts: {', '.join(failures)}")
        if failures:
            sys.exit(1)


if __name__ == "__main__":
    main()
