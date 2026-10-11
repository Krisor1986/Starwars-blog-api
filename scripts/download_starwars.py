"""Download the same first-page records shown by the React blog from SWAPI.tech."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

BASE_URL = "https://www.swapi.tech/api"
RESOURCE_URL = re.compile(r"https://(?:www\.)?swapi\.tech/api/[a-z]+/\d+/?$")
CATEGORIES = ("people", "planets", "vehicles")


def fetch_json(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def references(value):
    if isinstance(value, list):
        return {url for entry in value for url in references(entry)}
    if isinstance(value, str) and RESOURCE_URL.fullmatch(value):
        return {value}
    return set()


def main():
    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(
            fetch_json, [f"{BASE_URL}/{category}?page=1&limit=10&expanded=true" for category in CATEGORIES]
        ))
        categories = {}
        urls = set()
        for category, response in zip(CATEGORIES, responses):
            records = response["results"]
            if len(records) != 10:
                raise ValueError(f"Expected 10 {category} records")
            categories[category] = records
            for record in records:
                for value in record["properties"].values():
                    urls.update(references(value))
        urls = sorted(urls)
        details = executor.map(fetch_json, urls)
        names = {}
        for url, detail in zip(urls, details):
            properties = detail["result"]["properties"]
            names[url] = properties.get("name") or properties["title"]

    def resolve(value):
        if isinstance(value, list):
            return [resolve(entry) for entry in value]
        if isinstance(value, str):
            return names.get(value, value)
        return value

    snapshot = {"source": BASE_URL, "downloaded_at": datetime.now(timezone.utc).isoformat(), "categories": {}}
    for category, records in categories.items():
        snapshot["categories"][category] = []
        for record in records:
            properties = record["properties"]
            entry = {"swapi_id": str(record["uid"]), "properties": {key: resolve(value) for key, value in properties.items()}}
            if category == "people":
                homeworld = properties.get("homeworld")
                entry["homeworld_swapi_id"] = homeworld.rstrip("/").split("/")[-1] if homeworld else None
            snapshot["categories"][category].append(entry)
    destination = Path(__file__).resolve().parents[1] / "data" / "starwars.json"
    destination.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    print(f"Saved 30 live SWAPI records and resolved {len(names)} related resources to {destination}")


if __name__ == "__main__":
    main()
