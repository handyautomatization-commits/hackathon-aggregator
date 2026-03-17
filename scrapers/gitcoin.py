import requests


def fetch(limit=20):
    """Fetch open bounties from Gitcoin API."""
    url = "https://gitcoin.co/api/v0.1/bounties/"
    params = {"is_open": "true", "limit": limit, "order_by": "-web3_created"}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)"}
    results = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        for item in resp.json()[:limit]:
            results.append({
                "source": "Gitcoin",
                "title": item.get("title", "N/A"),
                "url": item.get("url", ""),
                "prize": f"{item.get('value_in_usdt', 'N/A')} USD",
                "deadline": item.get("expires_date", "N/A"),
                "raw": f"{item.get('title', '')} {item.get('description', '')}".strip()[:500],
            })
    except Exception as e:
        print(f"[Gitcoin] Error: {e}")
    return results
