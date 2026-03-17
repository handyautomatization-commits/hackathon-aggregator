import requests
import os


TOPICS = ["hackathon", "bounty", "coding-challenge"]


def fetch(limit=20):
    """Search GitHub repos tagged with hackathon/bounty topics."""
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    results = []
    try:
        for topic in TOPICS:
            url = "https://api.github.com/search/repositories"
            params = {
                "q": f"topic:{topic} created:>2025-01-01",
                "sort": "updated",
                "order": "desc",
                "per_page": 10,
            }
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            for item in resp.json().get("items", []):
                results.append({
                    "source": "GitHub",
                    "title": item.get("full_name", "N/A"),
                    "url": item.get("html_url", ""),
                    "prize": "N/A",
                    "deadline": "N/A",
                    "raw": f"{item.get('name', '')} {item.get('description', '')}".strip()[:500],
                })
            if len(results) >= limit:
                break
    except Exception as e:
        print(f"[GitHub] Error: {e}")
    return results[:limit]
