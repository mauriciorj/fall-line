import json
import os
import subprocess
import sys
import time
import importlib.util

CWD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(CWD)


def to_convex_sections(hours_data):
    sections = []
    for section_name, section_value in hours_data.items():
        if not section_value:
            continue
        first_val = next(iter(section_value.values()))
        if isinstance(first_val, dict):
            activities = []
            for activity_name, days in section_value.items():
                hours = [
                    {"day": day_name, "time": time_val}
                    for day_name, time_val in days.items()
                ]
                activities.append({"name": activity_name, "hours": hours})
            sections.append({"name": section_name, "activities": activities})
        else:
            hours = [
                {"day": day_name, "time": time_val}
                for day_name, time_val in section_value.items()
            ]
            sections.append({"name": section_name, "hours": hours})
    return sections


def main():
    json_path = os.path.join(CWD, "skisnowvalley", "hours-of-operation.json")
    if not os.path.isfile(json_path):
        print(f"No hours file found at {json_path}")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        hours_data = json.load(f)

    sections = to_convex_sections(hours_data)
    args = {
        "resortId": "snow-valley-ski-resort",
        "resortName": "Ski Snow Valley",
        "sourceUrl": "https://www.skisnowvalley.com/about/",
        "sections": sections,
        "fetchedAt": int(time.time() * 1000),
    }
    args_str = json.dumps(args, separators=(",", ":"))

    env = os.environ.copy()
    env["CONVEX_DEPLOYMENT"] = env.get("CONVEX_DEPLOYMENT") or "dev:astute-impala-848"

    cmd = [
        "node",
        "--use-system-ca",
        os.path.join(ROOT, "node_modules", "convex", "bin", "main.js"),
        "run",
        "resortHours:save",
        "--push",
        args_str,
    ]

    result = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
