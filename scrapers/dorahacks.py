import requests


def fetch(limit=20):
    """Fetch open hackathons from DoraHacks public API."""
    url = "https://dorahacks.io/api/v2/hackathon/"
    params = {"status": "open", "limit": limit, "offset": 0}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)"}
    results = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("data", data) if isinstance(data, dict) else data
        for item in items[:limit]:
            results.append({
                "source": "DoraHacks",
                "title": item.get("title", "N/A"),
                "url": f"https://dorahacks.io/hackathon/{item.get('id', '')}",
                "prize": str(item.get("total_prize", "N/A")),
                "deadline": item.get("end_time", "N/A"),
                "raw": str(item)[:500],
            })
    except Exception as e:
        print(f"[DoraHacks] Error: {e}")
    return results
