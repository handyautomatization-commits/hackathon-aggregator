import json
import os
from scrapers import devpost, dorahacks, gitcoin, mlh, reddit, github_search, twitter
import processor
import notifier

SEEN_FILE = "seen.json"


def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def deduplicate(items: list, seen: set) -> tuple[list, set]:
    new_items = []
    new_seen = set(seen)
    for item in items:
        key = item.get("url") or item.get("title", "")
        if key and key not in new_seen:
            new_items.append(item)
            new_seen.add(key)
    return new_items, new_seen


def main():
    print("=== Hackathon Aggregator Starting ===")
    seen = load_seen()

    # Collect from all sources
    all_items = []
    for scraper in [devpost, dorahacks, gitcoin, mlh, reddit, github_search, twitter]:
        name = scraper.__name__.split(".")[-1]
        try:
            items = scraper.fetch()
            print(f"[{name}] fetched {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"[{name}] failed: {e}")

    print(f"Total raw items: {len(all_items)}")

    # Deduplicate
    new_items, updated_seen = deduplicate(all_items, seen)
    print(f"New (unseen) items: {len(new_items)}")

    # Analyze with DeepSeek
    enriched = processor.analyze(new_items)
    relevant = [it for it in enriched if it.get("relevant", True)]
    print(f"Relevant items after filtering: {len(relevant)}")

    # Send to Telegram
    notifier.send_digest(relevant)

    # Save updated seen set
    save_seen(updated_seen)
    print("=== Done ===")


if __name__ == "__main__":
    main()
