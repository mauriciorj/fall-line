import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin


CRAWLER_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_GENERATOR = (
    CRAWLER_ROOT
    / "mountains"
    / "canada"
    / "ontario"
    / "brimacombe"
    / "json_generators"
    / "skiresort.py"
)
RESORT_URL_FIELDS = ("skiresortUrl", "skiresortInfoUrl", "sourceUrl", "url")
CONVEX_RESORT_FIELDS = (
    "name",
    "continent",
    "country",
    "region",
    "address",
    "website",
    "email",
    "phone",
    "rating",
)

sys.path.insert(0, str(CRAWLER_ROOT))
from convex_client import call_query, push_ski_resorts


def slugify(value, field_name):
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Missing usable {field_name}: {value!r}")
    return slug


def first_nonempty(*values):
    return next(
        (value.strip() for value in values if isinstance(value, str) and value.strip()),
        None,
    )


def location_value(resort, field, index):
    direct_value = first_nonempty(resort.get(field))
    if direct_value:
        return direct_value

    location = resort.get("location")
    if isinstance(location, list) and len(location) > index:
        return first_nonempty(location[index])
    return None


def source_url(resort):
    value = first_nonempty(*(resort.get(field) for field in RESORT_URL_FIELDS))
    if not value:
        raise ValueError(
            f"Missing skiresort.info URL for resort {resort.get('resortId') or resort.get('id')}"
        )
    return value


def normalize_resort(resort):
    if not isinstance(resort, dict):
        raise ValueError("Every list entry must be an object")

    resort_id = first_nonempty(resort.get("resortId"), resort.get("id"))
    if not resort_id:
        raise ValueError("Every resort must include resortId or id")

    country = location_value(resort, "country", 1)
    region = location_value(resort, "region", 2)
    if not country or not region:
        raise ValueError(f"Missing country or region for resort {resort_id}")

    return {
        **resort,
        "resortId": resort_id,
        "country": country,
        "region": region,
        "sourceUrl": source_url(resort),
    }


def load_resorts(path):
    with path.open("r", encoding="utf-8") as source:
        data = json.load(source)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [normalize_resort(resort) for resort in data]


def convex_record(resort):
    record = {
        "resortId": resort["resortId"],
        "published": False,
    }
    for field in CONVEX_RESORT_FIELDS:
        value = resort.get(field)
        if field == "rating" and isinstance(value, (int, float)):
            record[field] = value
        elif field != "rating" and isinstance(value, str) and value.strip():
            record[field] = value
    return record


def ensure_convex_registry(resort):
    existing = call_query(
        "resorts:getByResortId",
        {"resortId": resort["resortId"]},
    )
    if existing is not None:
        return False

    push_ski_resorts(
        [convex_record(resort)],
        function_path="resorts:saveMany",
    )
    return True


def render_skiresort_generator(resort_url):
    if not REFERENCE_GENERATOR.is_file():
        raise FileNotFoundError(f"Reference generator not found: {REFERENCE_GENERATOR}")

    content = REFERENCE_GENERATOR.read_text(encoding="utf-8")
    tracks_url = urljoin(resort_url.rstrip("/") + "/", "slope-offering/")
    replacements = {
        "RESORT_INFO_URL": resort_url,
        "TRACKS_INFO_URL": tracks_url,
    }
    for constant, value in replacements.items():
        content, count = re.subn(
            rf"^{constant} = .*?$",
            lambda _: f"{constant} = {json.dumps(value)}",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise ValueError(f"Could not replace {constant} in {REFERENCE_GENERATOR}")
    return content


def create_skiresort_generator(resort):
    country = slugify(resort["country"], "country")
    region = slugify(resort["region"], "region")
    resort_id = slugify(resort["resortId"], "resortId")
    resort_directory = CRAWLER_ROOT / "mountains" / country / region / resort_id
    generator_directory = resort_directory / "json_generators"
    generator_path = generator_directory / "skiresort.py"

    if not generator_path.exists():
        generator_directory.mkdir(parents=True, exist_ok=True)
        generator_path.write_text(
            render_skiresort_generator(resort["sourceUrl"]),
            encoding="utf-8",
        )
        return generator_path
    return None


def validate_unique_resorts(resorts):
    seen_ids = set()
    for resort in resorts:
        resort_id = resort["resortId"]
        if resort_id in seen_ids:
            raise ValueError(f"Duplicate resortId: {resort_id}")
        seen_ids.add(resort_id)


def process_file(path):
    resorts = load_resorts(path)
    validate_unique_resorts(resorts)

    created_registries = 0
    created_generators = 0
    for resort in resorts:
        if ensure_convex_registry(resort):
            created_registries += 1
            print(f"Created unpublished Convex registry: {resort['resortId']}")
        else:
            print(f"Convex registry exists: {resort['resortId']}")

        generator_path = create_skiresort_generator(resort)
        if generator_path:
            created_generators += 1
            print(f"Created generator: {generator_path}")
        else:
            print(f"Generator exists: {resort['resortId']}")

    return {
        "resorts": len(resorts),
        "createdRegistries": created_registries,
        "createdGenerators": created_generators,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create missing mountain skiresort generators from a JSON list."
    )
    parser.add_argument(
        "ski_resorts_list",
        type=Path,
        help="Path to a country/region/ski-resorts-list.json file",
    )
    args = parser.parse_args()

    result = process_file(args.ski_resorts_list.resolve())
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
