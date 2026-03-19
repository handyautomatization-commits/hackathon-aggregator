import requests


def fetch(limit=20):
    """Fetch open hackathons from Devpost JSON API."""
    url = "https://devpost.com/api/hackathons"
    params = {
        "status[]": "open",
        "order_by": "deadline",
        "per_page": limit,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)",
        "Accept": "application/json",
    }
    results = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("hackathons", [])[:limit]:
            results.append({
                "source": "Devpost",
                "title": item.get("title", "N/A"),
                "url": item.get("url", ""),
                "prize": item.get("prize_amount", "N/A"),
                "deadline": item.get("submission_period_dates", "N/A"),
                "raw": f"{item.get('title', '')} {item.get('tagline', '')} {item.get('themes', '')}".strip()[:500],
            })
    except Exception as e:
        print(f"[Devpost] Error: {e}")
    return results
