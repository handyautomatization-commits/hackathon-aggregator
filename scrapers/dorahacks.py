import feedparser
import requests
from bs4 import BeautifulSoup


def fetch(limit=20):
    """Fetch hackathons from DoraHacks via their explore page."""
    results = []

    # Try scraping the hackathon listing page
    url = "https://dorahacks.io/hackathon"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # DoraHacks renders client-side, but meta tags and JSON-LD may have data
        import json, re
        scripts = soup.find_all("script", type="application/json")
        for script in scripts:
            try:
                data = json.loads(script.string or "")
                # Look for hackathon data in any JSON structure
                text = json.dumps(data)
                if "hackathon" in text.lower() or "prize" in text.lower():
                    results.append({
                        "source": "DoraHacks",
                        "title": "DoraHacks Active Hackathons",
                        "url": "https://dorahacks.io/hackathon",
                        "prize": "See listing",
                        "deadline": "See listing",
                        "raw": text[:500],
                    })
                    break
            except Exception:
                continue

        # Fallback: just return the listing page as a pointer
        if not results:
            results.append({
                "source": "DoraHacks",
                "title": "DoraHacks Active Hackathons",
                "url": "https://dorahacks.io/hackathon",
                "prize": "Various",
                "deadline": "See website",
                "raw": "DoraHacks hosts Web3 hackathons and bounties. Visit the website to see currently open competitions.",
            })
    except Exception as e:
        print(f"[DoraHacks] Error: {e}")

    return results[:limit]
