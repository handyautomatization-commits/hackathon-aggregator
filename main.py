import json
import os
import re
from scrapers import devpost, dorahacks, gitcoin, mlh, reddit, github_search, twitter
import processor
import notifier


def _prize_value(prize_str) -> float:
    """Extract numeric USD value from a prize string for sorting. Returns 0 if unparseable."""
    if not prize_str or str(prize_str).strip() in ("N/A", "None", "", "See listing", "Various", "See website"):
        return 0.0
    raw = str(prize_str)
    # Strip currency symbols and commas, grab first number
    nums = re.findall(r"[\d,]+", raw.replace(",", ""))
    if not nums:
        return 0.0
    value = float(nums[0])
    # Rough INR→USD conversion so rupee prizes sort reasonably
    if "₹" in raw or "INR" in raw.upper():
        value /= 85
    return value


def filter_and_sort(items: list) -> list:
    """Keep only items with real prizes or prestige org. Sort by prize descending."""
    result = []
    for item in items:
        prize_val = _prize_value(item.get("prize"))
        is_prestige = item.get("prestige", False)
        if prize_val > 0 or is_prestige:
            item["_prize_val"] = prize_val
            result.append(item)
    result.sort(key=lambda x: x["_prize_val"], reverse=True)
    return result

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

    # Filter (prize > 0 or prestige) and sort by prize descending
    final = filter_and_sort(relevant)
    print(f"Final items after prize filter: {len(final)}")

    # Send to Telegram
    notifier.send_digest(final)

    # Save updated seen set
    save_seen(updated_seen)
    print("=== Done ===")


if __name__ == "__main__":
    main()
