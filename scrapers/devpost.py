import requests
from bs4 import BeautifulSoup


def fetch(limit=20):
    """Scrape active hackathons from Devpost."""
    url = "https://devpost.com/hackathons?challenge_type=all&status=open"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; HackathonBot/1.0)"}
    results = []
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("article.hackathon-thumb")[:limit]:
            title_el = card.select_one("h2")
            link_el = card.select_one("a.link-to-hackathon")
            prize_el = card.select_one(".prize-amount")
            deadline_el = card.select_one(".submission-period")
            results.append({
                "source": "Devpost",
                "title": title_el.get_text(strip=True) if title_el else "N/A",
                "url": link_el["href"] if link_el else "",
                "prize": prize_el.get_text(strip=True) if prize_el else "N/A",
                "deadline": deadline_el.get_text(strip=True) if deadline_el else "N/A",
                "raw": card.get_text(separator=" ", strip=True)[:500],
            })
    except Exception as e:
        print(f"[Devpost] Error: {e}")
    return results
